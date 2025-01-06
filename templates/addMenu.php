<?php
// Check if the form is submitted
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Get the opening hours
    $openingFrom = htmlspecialchars($_POST['opening_from']);
    $openingTo = htmlspecialchars($_POST['opening_to']);

    // Get the postcodes
    $postcodes = $_POST['postcode'];

    // Get the menu items
    $appetizers = [];
    $mains = [];
    $desserts = [];
    $drinks = [];

    // Loop through appetizers
    if (isset($_POST['appetizer_name'])) {
        foreach ($_POST['appetizer_name'] as $index => $name) {
            $appetizers[] = [
                'name' => htmlspecialchars($name),
                'description' => htmlspecialchars($_POST['appetizer_description'][$index]),
                'price' => htmlspecialchars($_POST['appetizer_price'][$index]),
            ];
        }
    }

    // Loop through main dishes
    if (isset($_POST['main_name'])) {
        foreach ($_POST['main_name'] as $index => $name) {
            $mains[] = [
                'name' => htmlspecialchars($name),
                'description' => htmlspecialchars($_POST['main_description'][$index]),
                'price' => htmlspecialchars($_POST['main_price'][$index]),
            ];
        }
    }

    // Loop through desserts
    if (isset($_POST['dessert_name'])) {
        foreach ($_POST['dessert_name'] as $index => $name) {
            $desserts[] = [
                'name' => htmlspecialchars($name),
                'description' => htmlspecialchars($_POST['dessert_description'][$index]),
                'price' => htmlspecialchars($_POST['dessert_price'][$index]),
            ];
        }
    }

    // Loop through drinks
    if (isset($_POST['drink_name'])) {
        foreach ($_POST['drink_name'] as $index => $name) {
            $drinks[] = [
                'name' => htmlspecialchars($name),
                'price' => htmlspecialchars($_POST['drink_price'][$index]),
            ];
        }
    }

    // Print the submitted data (for debugging or testing)
    echo "<h1>Submitted Data</h1>";
    echo "<h2>Opening Hours: $openingFrom to $openingTo</h2>";
    echo "<h2>Postcodes:</h2>";
    echo "<ul>";
    foreach ($postcodes as $postcode) {
        echo "<li>" . htmlspecialchars($postcode) . "</li>";
    }
    echo "</ul>";

    echo "<h2>Appetizers:</h2>";
    foreach ($appetizers as $appetizer) {
        echo "<p>Name: {$appetizer['name']}, Description: {$appetizer['description']}, Price: {$appetizer['price']}</p>";
    }

    echo "<h2>Main Dishes:</h2>";
    foreach ($mains as $main) {
        echo "<p>Name: {$main['name']}, Description: {$main['description']}, Price: {$main['price']}</p>";
    }

    echo "<h2>Desserts:</h2>";
    foreach ($desserts as $dessert) {
        echo "<p>Name: {$dessert['name']}, Description: {$dessert['description']}, Price: {$dessert['price']}</p>";
    }

    echo "<h2>Drinks:</h2>";
    foreach ($drinks as $drink) {
        echo "<p>Name: {$drink['name']}, Price: {$drink['price']}</p>";
    }
} else {
    // Redirect to the form if accessed directly
    header('Location: index.html');
    exit;
}
?>
