// Loads up the Trello iframe and applies the styling
const t = window.TrelloPowerUp.iframe();


document.addEventListener("DOMContentLoaded", function () {



  const dropdown = document.getElementById('boardDropdown');
  const dropdownList = document.getElementById('listDropdown');



  async function getLists() {
    const selectedValue = dropdown.value;

    // Clear dropdown2 while loading new options
    //clearDropdown(dropdownList);

    // Step 3: Second API call to populate dropdown2 based on dropdown1 value
    if (selectedValue) {
      await fetch(`http://127.0.0.1:8123/getFilteredListsOnBoard?boardID=${selectedValue}`)
        .then(response => response.json())
        .then(data => {
          populateDropdown(dropdownList, data);
        })
        .catch(error => console.error('Error fetching second API:', error));
    }
  }


  // Step 1: First API call to populate dropdown1
  fetch('http://127.0.0.1:8123/getBoards')
    .then(response => response.json())
    .then(data => {
      populateDropdown(dropdown, data);
      getLists()
    })
    .catch(error => console.error('Error fetching first API:', error));

  // Step 2: Event listener for dropdown1 changes
  dropdown.addEventListener('change', () => {
    getLists()
  });

  // Utility function to populate a dropdown
  function populateDropdown(dropdown, options) {
    dropdown.innerHTML = ''; // Clear existing options
    options.forEach(option => {
      const opt = document.createElement('option');
      opt.value = option.id; // Adjust based on your API response structure
      opt.textContent = option.name; // Adjust based on your API response structure
      dropdown.appendChild(opt);
    });
  }

});