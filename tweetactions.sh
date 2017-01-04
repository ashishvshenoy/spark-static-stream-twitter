/home/ubuntu/assignment2/question_b/streamer.sh &
sleep 5
spark-submit --verbose /home/ubuntu/assignment2/question_b/b3_tweetcount.py /user/ubuntu/monitoring2 &
