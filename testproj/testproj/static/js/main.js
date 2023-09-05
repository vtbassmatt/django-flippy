function sendCommand(command) {
  const options = {
    method: 'POST',
    headers: {
      'User-Agent': 'insecure-flippy-demo/6.6.6',
    }
  };
  const url = `/control/${command}`;
  fetch(url, options)
  .then((response) => {
    if (response.status != 201) {
      alert(`Got ${response.status} ${response.statusText}`);
      return;
    }

    location.reload();
  });
}