<?php
    require_once('inventoryclass.php');
    $inventoryorkestra = new Inventoryorkestra();
    $users = $inventoryorkestra -> getUsers();
    print_r($users);

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!--==================== CSS ====================-->
    <link rel="stylesheet" href="css/styles.css">
    <!--==================== UNPKG ICONS ====================-->
    <link rel="stylesheet" href="https://unpkg.com/boxicons@latest/css/boxicons.min.css">
    <!--==================== REMIX ICON ====================-->
    <link href="https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css" rel="stylesheet"/>
    <!--==================== FONTS ====================-->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap" rel="stylesheet">
    <title>Orkestra Inventory PC</title>
</head>
<body>
    
</body>
</html>