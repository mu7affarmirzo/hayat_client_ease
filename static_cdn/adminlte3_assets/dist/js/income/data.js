/* eslint-disable no-alert */

// to run php code run this command:
// php -S 0.0.0.0:8080

$(() => {
  // Function to load data and populate the table
  function populateTable(users, tableId, withRemove = false) {
    const $table = $(`#${tableId}`)
    const $tbody = $table.find('tbody')

    // Destroy the existing DataTable, if it exists
    if ($.fn.DataTable.isDataTable(`#${tableId}`)) {
      $table.DataTable().destroy()
    }

    // Clear the table contents
    $tbody.empty()

    // Append new rows
    users.forEach(rowData => {
      const $row = $(`<tr data-id="${rowData.id}" class="cursor-pointer"></tr>`)

      $row.append(`<td>${rowData.name}</td>`)
      $row.append(`<td>${rowData.age}</td>`)
      $row.append(`<td>${rowData.country}</td>`)
      if (withRemove) {
        $row.append(`<td><button class="remove-btn" data-id="${rowData.id}">Remove</button></td>`) // Add button to the last td
      }

      $tbody.append($row)
    })

    // Reinitialize the DataTable
    $table.DataTable()
  }

  function removeItem(id, fileName) {
    $.ajax({
      url: 'http://0.0.0.0:8080/removeItem.php', // Server-side script to handle removal
      type: 'POST',
      data: { id, jsonFile: fileName }, // Send the ID of the user to be removed
      success(response) {
        // Handle successful removal
        // eslint-disable-next-line no-console
        console.log('User removed successfully:', response)
        // Optionally, update the table with the updated data
        // populateTable(response, )
      },
      error(xhr, status, error) {
        // eslint-disable-next-line no-console
        console.error('Error removing user:', status, error)
      }
    })
  }

  function addItem(item, fileName, tableId) {
    $.ajax({
      url: 'http://0.0.0.0:8080/addItem.php', // URL of the server-side script
      type: 'POST',
      data: { jsonData: item, jsonFile: fileName }, // Send the object directly
      success(response) {
        // eslint-disable-next-line no-console
        console.log('Response:', response)
        populateTable(response, tableId, true)
      },
      error(xhr, status, error) {
        // eslint-disable-next-line no-console
        console.error('Error:', status, error)
      }
    })
    // eslint-disable-next-line no-console
    console.log({ item, id: item.id, name: item.name })
  }

  $.ajax({
    url: 'data.json', // Make sure this path is correct
    dataType: 'json',
    success(data) {
      populateTable(data, 'example2', true)
    },
    error(xhr, status, error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching data:', status, error)
      // alert(`Failed to load data: ${status} - ${error}`)
    }
  })

  $.ajax({
    url: 'list-data.json', // Make sure this path is correct
    dataType: 'json',
    success(data) {
      populateTable(data, 'example1')
    },
    error(xhr, status, error) {
      // eslint-disable-next-line no-console
      console.error('Error fetching data:', status, error)
      // alert(`Failed to load data: ${status} - ${error}`)
    }
  })

  $('#example1 tbody').on('click', 'tr', function () {
    // Get the data from the clicked row
    const rowData = $(this).find('td').map(function () {
      return $(this).text()
    }).get()
    const id = $(this).data('id')

    removeItem(Number(id), 'list-data.json')
    addItem({
      id: Number(id),
      name: rowData[0],
      age: Number(rowData[1]),
      country: rowData[2]
    }, 'data.json', 'example2')
    // Example: Log the data to console
    // console.log('Clicked row data:', rowData)
  })

  $('#example2 tbody').on('click', 'tr .remove-btn', function () {
    // Get the data from the clicked button
    const itemId = $(this).data('id')

    removeItem(Number(itemId), 'data.json')
  })

  $('body').on('click', '#add-item', () => {
    const name = prompt('Enter name', '')
    const agePrompt = prompt('Enter age', '')
    const age = !Number.isNaN(agePrompt) ? agePrompt : 0
    const country = prompt('Enter country name', '')

    if (name && age && country) {
      addItem({
        id: Number(new Date(Date.now())),
        name,
        age,
        country
      }, 'data.json', 'example2')
    }
  })
})
