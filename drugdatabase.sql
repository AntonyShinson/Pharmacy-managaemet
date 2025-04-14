CREATE DATABASE IF NOT EXISTS drugdatabase;
USE drugdatabase;

-- Customers Table
CREATE TABLE IF NOT EXISTS Customers (
  C_Name TEXT NOT NULL,
  C_Password TEXT NOT NULL,
  C_Email TEXT PRIMARY KEY NOT NULL
);

-- Drugs Table
CREATE TABLE IF NOT EXISTS Drugs (
  D_id INTEGER PRIMARY KEY AUTOINCREMENT,
  D_Name TEXT NOT NULL UNIQUE,
  D_ExpDate TEXT NOT NULL,
  D_Qty INTEGER NOT NULL,
  D_Price REAL NOT NULL
);

-- Orders Table
CREATE TABLE IF NOT EXISTS Orders (
  O_id INTEGER PRIMARY KEY AUTOINCREMENT,
  O_Name TEXT NOT NULL,
  O_Items TEXT NOT NULL,
  O_Qty INTEGER NOT NULL,
  O_TotalPrice REAL NOT NULL
);

-- Sample Data
INSERT INTO Customers (C_Name, C_Password, C_Email) VALUES
('admin', 'admin123', 'admin@example.com'),
('user1', 'password1', 'user1@example.com');

INSERT INTO Drugs (D_Name, D_ExpDate, D_Qty, D_Price) VALUES
('Paracetamol', '2025-12-31', 100, 10.5),
('Ibuprofen', '2024-08-15', 50, 15.0);

-- Create a trigger to update inventory when an order is placed
DELIMITER //

CREATE TRIGGER reduce_stock AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    UPDATE Drugs
    SET D_Qty = D_Qty - NEW.O_Qty
    WHERE D_Name = NEW.O_Items;
END;
//

DELIMITER ;
