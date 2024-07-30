fname=`basename $0`
pdir=`cd -P $(dirname $0); pwd`

rm -rf /opt/ai_env
mkdir -p /opt/ai_env
mkdir -p /opt/lancedb_cache
mkdir -p /opt/lancedb_data
tar -zxvf $pdir/conda/ai_env.tar.gz -C /opt/ai_env/
rm -rf /root/.paddleocr
rm -rf /root/nltk_data
mv -f $pdir/resources/.paddleocr $pdir/resources/nltk_data /root
tar -zxvf $pdir/resources/cuda-12.1.tar.gz -C /usr/local/
rm -f $pdir/resources/cuda-12.1.tar.gz
rm -rf /opt/paddle_server_for_ai_env
mv -f $pdir/server/paddle_server_for_ai_env /opt/
cp -rf /opt/paddle_server_for_ai_env/etc/* /root/lcm-guard/etc/guard/conf.d/
rm -f /opt/ai_env/lib/libstdc++.so /opt/ai_env/lib/libstdc++.so.6
cd /opt/ai_env/lib
ln -s libstdc++.so.6.0.31 libstdc++.so.6
ln -s libstdc++.so.6.0.31 libstdc++.so

rm -f /root/lcm-guard/etc/guard/conf.d/ppvector_server.xml
lcm_guard --kill-forever ppvector_server
sleep 5
lcm_guard --reload
sleep 10
lcm_guard --kill paddle_server
sleep 5
lcm_guard --kill gpu_monitor
sleep 5
lcm_guard --kill vectordb_server
sleep 5