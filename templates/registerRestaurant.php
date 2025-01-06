<?php
// Check if the form is submitted
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Validate and sanitize the input fields
    $name = htmlspecialchars($_POST['name']);
    $description = htmlspecialchars($_POST['description']);
    $address = htmlspecialchars($_POST['address']);

    // Handle the uploaded file
    if (isset($_FILES['picture']) && $_FILES['picture']['error'] === UPLOAD_ERR_OK) {
        $uploadDir = 'uploads/'; // Directory to save uploaded files
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0777, true); // Create the directory if it doesn't exist
        }

        $fileTmpPath = $_FILES['picture']['tmp_name'];
        $fileName = basename($_FILES['picture']['name']);
        $fileExtension = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

        // Allowed file types
        $allowedExtensions = ['jpg', 'jpeg', 'png', 'gif'];

        if (in_array($fileExtension, $allowedExtensions)) {
            $uniqueFileName = uniqid('restaurant_', true) . '.' . $fileExtension;
            $filePath = $uploadDir . $uniqueFileName;

            if (move_uploaded_file($fileTmpPath, $filePath)) {
                echo "<h1>Restaurant Registered Successfully</h1>";
                echo "<p>Name: $name</p>";
                echo "<p>Description: $description</p>";
                echo "<p>Address: $address</p>";
                echo "<p>Picture:</p>";
                echo "<img src='$filePath' alt='Restaurant Picture' style='max-width: 100%; height: auto;'>";

                // Save the data to a database (optional, depends on your requirements)
                // Example:
                // $db = new mysqli('host', 'user', 'password', 'database');
                // $stmt = $db->prepare("INSERT INTO restaurants (name, description, address, picture) VALUES (?, ?, ?, ?)");
                // $stmt->bind_param('ssss', $name, $description, $address, $filePath);
                // $stmt->execute();
                // $stmt->close();
                // $db->close();
            } else {
                echo "<p>Error: Failed to save the uploaded picture.</p>";
            }
        } else {
            echo "<p>Error: Invalid file type. Only JPG, JPEG, PNG, and GIF files are allowed.</p>";
        }
    } else {
        echo "<p>Error: Please upload a picture.</p>";
    }
} else {
    // Redirect to the form if accessed directly
    header('Location: index.html');
    exit;
}
?>
