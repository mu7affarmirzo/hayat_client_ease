<?php

header('Access-Control-Allow-Origin: *');
        if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
            $headers=getallheaders();
            @$ACRH=$headers["Access-Control-Request-Headers"];
            header("Access-Control-Allow-Headers: $ACRH");
        }

header("Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE");

// Get the ID of the user to be removed from the request
$id = $_POST['id'];

// JSON file name
$jsonFileName = $_POST['jsonFile'];

// Read the JSON file
$data = file_get_contents($jsonFileName);
$users = json_decode($data, true);

// Remove the user with the specified ID from the array
foreach ($users as $key => $user) {
    if ($user['id'] == $id) {
        unset($users[$key]);
        break;
    }
}

// Encode the updated array back to JSON
$jsonData = json_encode(array_values($users));

// Write the updated JSON data back to the file
file_put_contents($jsonFileName, $jsonData);

// Optionally, you can send back the updated data
echo $jsonData;
?>