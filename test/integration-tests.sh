ANSW=$(curl http://127.0.0.1:5001/)
if [ "$ANSW" != "Hello, World!" ]; then
  exit 1
else
  echo "Integration Test PASS"
fi
