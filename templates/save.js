// fetch('https://jsonplaceholder.typicode.com/posts')
//   .then(response => {
//     if (!response.ok) {
//       throw new Error(`HTTP error! Status: ${response.status}`);
//     }
//     return response.json();
//   })
//   .then(data => {
//     console.log(data); // Handle the response data
//   })
//   .catch(error => {
//     console.error('There was an error!', error);
//   });



// // This code sample uses the 'node-fetch' library:
// // https://www.npmjs.com/package/node-fetch
// const fetch = require('node-fetch');

// fetch('https://api.trello.com/1/cards/{id}/pluginData?key=APIKey&token=APIToken', {
//   method: 'GET'
// })
//   .then(response => {
//     console.log(
//       `Response: ${response.status} ${response.statusText}`
//     );
//     return response.text();
//   })
//   .then(text => console.log(text))
//   .catch(err => console.error(err));


var t = TrelloPowerUp.iframe();

t.get()

t.render(function () {
    t.sizeTo("#estimate").done();
  });
  