docker run --gpus all \
  -w /app \
  --rm \
  -p 8888:8888 \
  -p 8008:8008 \
  -v $(pwd)/GAN:/app\
  -v $(pwd)/data:/data \
  test bash -c "python  /app/main.py && tensorboard --logdir /app/lightning_logs --port 8008"