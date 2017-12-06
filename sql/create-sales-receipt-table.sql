use surfaces;

CREATE TABLE IF NOT EXISTS SalesReceipts(
        SaleNo INT NOT NULL AUTO_INCREMENT,
	Date DATE,
	Total FLOAT NOT NULL,
	NumItems INT NOT NULL,
	CustName VARCHAR(40),
	CustAddress VARCHAR(100),
	CustPhone DECIMAL(15),
	SoldBy VARCHAR(15) NOT NULL,
	PaymentMethod VARCHAR(20) NOT NULL,
	PRIMARY KEY (SaleNo)	
);


CREATE TABLE IF NOT EXISTS ProductSales(
       SaleNo INT NOT NULL,
       Product VARCHAR(100) NOT NULL
);
