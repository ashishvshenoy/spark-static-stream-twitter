from __future__ import print_function

import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.functions import window
from pyspark.sql.types import StructType
from pyspark.sql.streaming import DataStreamReader

if __name__ == "__main__":
    if len(sys.argv) != 2 :
        msg = ("Usage: b1_tweetcount.py <monitoring_dir> ")
        print(msg, file=sys.stderr)
        exit(-1)

    windowSize = "3600"
    slideSize = "1800"
    if slideSize > windowSize:
        print("<slide duration> must be less than or equal to <window duration>", file=sys.stderr)
    windowDuration = '{} seconds'.format(windowSize)
    slideDuration = '{} seconds'.format(slideSize)
    monitoring_dir = sys.argv[1]

    spark = SparkSession\
        .builder\
        .appName("InteractionCount")\
        .config("spark.eventLog.enabled","true")\
        .config("spark.eventLog.dir","hdfs://10.254.0.33:8020/user/ubuntu/applicationHistory")\
        .master("spark://10.254.0.33:7077")\
        .getOrCreate()

    userSchema = StructType().add("userA","string").add("userB","string").add("timestamp","timestamp").add("interaction","string")
    twitterIDSchema = StructType().add("userA","string")
    twitterIDs = spark.read.schema(twitterIDSchema).csv('/user/ubuntu/twitterIDs.csv')
    csvDF = spark\
        .readStream \
	.schema(userSchema) \
	.csv(monitoring_dir)
    joinedDF = csvDF.join(twitterIDs,"userA")

    interactions = joinedDF.select(joinedDF['userA'],joinedDF['interaction']);

    windowedCounts = interactions.groupBy(interactions.userA).count()

    query = windowedCounts\
        .writeStream\
        .outputMode('complete')\
        .format('console')\
	.option('truncate','false')\
	.option('numRows','10000')\
        .trigger(processingTime='5 seconds')\
        .start()

    query.awaitTermination()
