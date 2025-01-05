// Loads up the Trello iframe and applies the styling
const t = window.TrelloPowerUp.iframe();



document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.getElementById('boardDropdown');
  const dropdownList = document.getElementById('listDropdown');
 
  // Function to fetch data and populate the dropdown
  async function fetchData() {
    await fetch('http://127.0.0.1:8123/getBoards') // Replace with your API URL
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        //console.log(response.json())
        return response.json();
      })
      .then(data => {
        populateDropdown(data);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  }




  // Function to populate dropdown
  async function populateDropdown(data) {
      // generate options based on the response
      for (i = 0, len = data.length; i < len; i++) {
        const option = document.createElement('option');
        option.value = data[i].id; // Adjust based on API response structure
        option.text = data[i].name;
        dropdown.appendChild(option);
      } 
      // const option = document.createElement('option');
      // option.value = 'Diplomski'; // Adjust based on API response structure
      // option.text = 'Diplomski';
      // const option_2 = document.createElement('option');
      // option_2.value = 'Vikendica';
      // option_2.text = 'Vikendica';
      // dropdown.appendChild(option);
      // dropdown.appendChild(option_2);


      // const listOption = document.createElement('option')
      // listOption.value = 'Backlog';
      // listOption.text = 'Backlog';
      // dropdownList.appendChild(listOption)
      // const listOption_2 = document.createElement('option')
      // listOption_2.value = 'TO DO';
      // listOption_2.text = 'TO DO';
      // dropdownList.appendChild(listOption_2)
  }


  // Call fetch function on load
  fetchData();
});







// t.render(function () {
//   t.sizeTo("#estimate").done();
// });
