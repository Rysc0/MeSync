// // This code sample uses the 'node-fetch' library:
// // https://www.npmjs.com/package/node-fetch




// var t = TrelloPowerUp.iframe();

// t.get()

document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.getElementById('boardDropdown');
  const dropdownList = document.getElementById('listDropdown');
 
  // Function to fetch data and populate the dropdown
  // function fetchData() {
  //   fetch('https://api.trello.com/1/members/me/boards?key={{API_KEY}}&token={{TOKEN}}') // Replace with your API URL
  //     .then(response => {
  //       if (!response.ok) {
  //         throw new Error(`HTTP error! status: ${response.status}`);
  //       }
  //       return response.json();
  //     })
  //     .then(data => {
  //       populateDropdown(data);
  //     })
  //     .catch(error => {
  //       console.error('Error fetching data:', error);
  //     });
  // }




  // Function to populate dropdown
  function populateDropdown(data) {
    
      const option = document.createElement('option');
      option.value = 'Diplomski'; // Adjust based on API response structure
      option.text = 'Diplomski';
      const option_2 = document.createElement('option');
      option_2.value = 'Vikendica';
      option_2.text = 'Vikendica';
      dropdown.appendChild(option);
      dropdown.appendChild(option_2);


      const listOption = document.createElement('option')
      listOption.value = 'Backlog';
      listOption.text = 'Backlog';
      dropdownList.appendChild(listOption)
      const listOption_2 = document.createElement('option')
      listOption_2.value = 'TO DO';
      listOption_2.text = 'TO DO';
      dropdownList.appendChild(listOption_2)
  }

  // Call fetch function on load
  populateDropdown();
});







// t.render(function () {
//   t.sizeTo("#estimate").done();
// });
