<?php

Class  InventoryOrkestra {
    
    private $server = "mysql:host=localhost;dbname=inventory_orkestra";
    private $user = "root";
    private $pass = "admin";
    private $option = array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC);
    protected $con;
    
    public function openConnection()
    {
        try {
            $this->con = new PDO($this->server, $this->user, $this->pass, $this->option);
            return $this->con;
        }catch (PDOException $e) {
            echo "There is a problem in the connection : ". $e-> getMessage();
        }
    }
    public function closeConnection()
    {
        $this ->con = null;
    }

    public function getUsers()
    {
        $connection = $this -> openConnection();
        $stmt = $connection -> prepare('SELECT * FROM user');
        $stmt -> execute();
        $users = $stmt->fetchAll();
        $userCount = $stmt->rowCount();
        
        if($userCount > 0)
        {
            return $users;
        }else{
            return 0;
        }
    }
}

