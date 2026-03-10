const socket = new WebSocket("ws://127.0.0.1:8000/ws/price/AAPL");

socket.onmessage = function (event) {
  const data = JSON.parse(event.data);

  console.log(data);

  document.getElementById("price").innerText = data.last;
};
