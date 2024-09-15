function onEdit(e) {
  Logger.log("onEdit triggered");

  if (!e) {
    Logger.log("No event object.");
    return;
  }

  var sheet = e.source.getActiveSheet();   // Get the active sheet
  var row = e.range.getRow();              // Get the row number of the edited cell
  var lastColumn = sheet.getLastColumn();  // Get the last column number of the sheet
  var range = sheet.getRange(row, 1, 1, lastColumn);  // Get the entire row (from the first column to the last)
  var values = range.getValues();  // Get the values of the entire row

  // Log the values to verify what's being sent
  Logger.log("Edited row values: " + JSON.stringify(values));

  // Create a JSON object with the row number and the entire row's values
  var payload = {
    "row": row,
    "values": values  // Send the entire row of values
  };

  // Check if the entire row is empty (i.e., if the user added a new row without content yet)
  var rowEmpty = true;
  for (var i = 0; i < values[0].length; i++) {
    if (values[0][i] !== "") {
      rowEmpty = false;
      break;
    }
  }

  // If the row is not empty, send the data to the Flask server for conflict resolution
  if (!rowEmpty) {
    checkForConflicts(payload);
  }
}

// Function to check if there's a conflict between Google Sheets data and the database
function checkForConflicts(payload) {
  var options = {
    'method': 'post',
    'contentType': 'application/json',  // Set Content-Type to JSON
    'payload': JSON.stringify(payload)  // Convert the payload to a JSON string
  };

  try {
    // Send a request to the Flask server to check if there is a conflict
    var checkResponse = UrlFetchApp.fetch('https://e5c0-2401-4900-1f25-2e8c-6496-3bc4-fb21-c731.ngrok-free.app/check-database', options);
    var checkData = JSON.parse(checkResponse.getContentText());

    // If there is a conflict, revert the Google Sheets row to the database data
    if (checkData.conflict) {
      Logger.log("Conflict detected. Database data will be preferred.");
      revertGoogleSheetRow(payload.row, checkData.database_row);
    } else {
      // If no conflict, proceed with sending the data to the database
      sendToDatabase(payload);
    }
  } catch (err) {
    Logger.log("Error occurred during conflict check: " + err.toString());
  }
}

// Function to send data to the Flask server (if no conflict)
function sendToDatabase(payload) {
  var options = {
    'method' : 'post',
    'contentType': 'application/json',  // Set Content-Type to JSON
    'payload' : JSON.stringify(payload)  // Convert the payload to a JSON string
  };

  // Send the request to your Flask server
  try {
    var response = UrlFetchApp.fetch('https://e5c0-2401-4900-1f25-2e8c-6496-3bc4-fb21-c731.ngrok-free.app/update-database', options);
    Logger.log("Response from server: " + response.getContentText());
  } catch (err) {
    Logger.log("Error occurred: " + err.toString());
  }
}

// Function to revert the Google Sheets row to the database data if there is a conflict
function revertGoogleSheetRow(row, databaseRow) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var lastColumn = sheet.getLastColumn();
  sheet.getRange(row, 1, 1, lastColumn).setValues([databaseRow]);
  Logger.log("Google Sheets row reverted to database data.");
}
