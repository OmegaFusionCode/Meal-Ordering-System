
--
-- Drop all tables
--

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `students`;
DROP TABLE IF EXISTS `allergens`;
DROP TABLE IF EXISTS `student_allergens`;
DROP TABLE IF EXISTS `ingredients`;
DROP TABLE IF EXISTS `ingredient_allergens`;
DROP TABLE IF EXISTS `options`;
DROP TABLE IF EXISTS `option_ingredients`;
DROP TABLE IF EXISTS `days`;
DROP TABLE IF EXISTS `menu_options`;
DROP TABLE IF EXISTS `orders`;

SET FOREIGN_KEY_CHECKS = 1;



--
-- Defines the table structure for the 'students' table
--

CREATE TABLE `students` (
  `studentID` int(11) NOT NULL auto_increment,
  `firstname` char(35) NOT NULL default '',
  `lastname` char(35) NOT NULL default '',
  `tutorgroup` char(6) NOT NULL default '',
  `password` char(35) NOT NULL default '',
  `balance` decimal(6,2) NOT NULL default 0,
   PRIMARY KEY  (`studentID`)
) AUTO_INCREMENT = 1000;

--
-- Defines the table structure for the 'allergens' table
--

CREATE TABLE `allergens` (
  `allergenID` int(11) NOT NULL auto_increment,
  `name` char(35) NOT NULL default '',
  PRIMARY KEY (`allergenID`)
) AUTO_INCREMENT = 6001;

--
-- Defines the table structure for the 'student_allergens' junction table
--

CREATE TABLE `student_allergens` (
  `studentID` int(11) NOT NULL default 0,
  `allergenID` int(11) NOT NULL default 0,
  FOREIGN KEY (`studentID`) REFERENCES `students`(`studentID`),
  FOREIGN KEY (`allergenID`) REFERENCES `allergens`(`allergenID`)
);

--
-- Defines the table structure for the 'ingredients' table
--

CREATE TABLE `ingredients` (
  `ingredientID` int(11) NOT NULL auto_increment,
  `name` char(35) NOT NULL default '',
  `pricePerKG` decimal(6,2) NOT NULL default 0,
  PRIMARY KEY (`ingredientID`)
) AUTO_INCREMENT = 5000;

--
-- Defines the table structure for the 'ingredient_allergens' junction table
--

CREATE TABLE `ingredient_allergens` (
  `ingredientID` int(11) NOT NULL default 0,
  `allergenID` int(11) NOT NULL default 0,
  FOREIGN KEY (`ingredientID`) REFERENCES `ingredients`(`ingredientID`),
  FOREIGN KEY (`allergenID`) REFERENCES `allergens`(`allergenID`)
);

--
-- Defines the table structure for the 'options' table
--

CREATE TABLE `options` (
  `optionID` int(11) NOT NULL auto_increment,
  `name` char(52) NOT NULL default '',
  `price` decimal(6,2) NOT NULL default 0,
  PRIMARY KEY  (`optionID`)
) AUTO_INCREMENT = 3000;

--
-- Defines the table structure for the 'option_ingrdients' junction table
--

CREATE TABLE `option_ingredients` (
  `optionID` int(11) NOT NULL default 0,
  `ingredientID` int(11) NOT NULL default 0,
  `quantity`  int(11) NOT NULL default 0,
  FOREIGN KEY (`optionID`) REFERENCES `options`(`optionID`),
  FOREIGN KEY (`ingredientID`) REFERENCES `ingredients`(`ingredientID`)
);

--
-- Defines the table structure for the 'days' table
--

CREATE TABLE `days` (
    `dayID` int(11) NOT NULL auto_increment,
    `timestamp` int(11) NOT NULL default 0,
    `temperature` int(11) default NULL,
    PRIMARY KEY (`dayID`)
) AUTO_INCREMENT = 4000;

--
-- Defines the table structure for the 'menu_options' junction table
--

CREATE TABLE `menu_options` (
    `dayID` int(11) NOT NULL default 0,
    `optionID` int(11) NOT NULL default 0,
    FOREIGN KEY (`dayID`) REFERENCES `days`(`dayID`),
    FOREIGN KEY (`optionID`) REFERENCES `options`(`optionID`)
);

--
-- Defines the table structure for the 'orders' table
--

CREATE TABLE `orders` (
    `orderID` int(11) NOT NULL auto_increment,
    `studentID` int(11) NOT NULL default 0,
    `optionID` int(11) NOT NULL default 0,
    `dayID` int(11) NOT NULL default 0,
    PRIMARY KEY (`orderID`),
    FOREIGN KEY (`studentID`) REFERENCES `students`(`studentID`),
    FOREIGN KEY (`optionID`) REFERENCES `options`(`optionID`),
    FOREIGN KEY (`dayID`) REFERENCES `days`(`dayID`)
) AUTO_INCREMENT = 2000;




--
-- Data for the 'allergens' table
--

INSERT INTO `allergens` VALUES (6001, "wheat");
INSERT INTO `allergens` VALUES (6002, "shellfish");
INSERT INTO `allergens` VALUES (6003, "eggs");
INSERT INTO `allergens` VALUES (6004, "fish");
INSERT INTO `allergens` VALUES (6005, "peanuts");
INSERT INTO `allergens` VALUES (6006, "soybeans");
INSERT INTO `allergens` VALUES (6007, "milk");
INSERT INTO `allergens` VALUES (6008, "nuts");
INSERT INTO `allergens` VALUES (6009, "celery");
INSERT INTO `allergens` VALUES (6010, "mustard");
INSERT INTO `allergens` VALUES (6011, "sesame");
INSERT INTO `allergens` VALUES (6012, "sulphur dioxide");
INSERT INTO `allergens` VALUES (6013, "lupin");
INSERT INTO `allergens` VALUES (6014, "molluscs");

--
-- Data for the 'ingredients' table
--

INSERT INTO `ingredients` VALUES (5000, 'potato', 0.60);
INSERT INTO `ingredients` VALUES (5001, 'cod', 10.00);
INSERT INTO `ingredients` VALUES (5002, 'pasta', 0.50);
INSERT INTO `ingredients` VALUES (5003, 'minced beef', 4.00);
INSERT INTO `ingredients` VALUES (5004, 'tomato', 1.50);
INSERT INTO `ingredients` VALUES (5005, 'chicken', 4.00);
INSERT INTO `ingredients` VALUES (5006, 'brocolli', 1.50);
INSERT INTO `ingredients` VALUES (5007, 'curry sauce', 3.00);
INSERT INTO `ingredients` VALUES (5008, 'rice', 1.20);
INSERT INTO `ingredients` VALUES (5009, 'wrap', 3.00);
INSERT INTO `ingredients` VALUES (5010, 'mayonnaise', 1.50);
INSERT INTO `ingredients` VALUES (5011, 'salad leaf', 1.00);
INSERT INTO `ingredients` VALUES (5012, 'bread', 1.50);
INSERT INTO `ingredients` VALUES (5013, 'burger', 5.00);
INSERT INTO `ingredients` VALUES (5014, 'lettuce', 0.60);
INSERT INTO `ingredients` VALUES (5015, 'salad dressing', 1.50);
INSERT INTO `ingredients` VALUES (5016, 'pork', 4.00);
INSERT INTO `ingredients` VALUES (5017, 'beans', 0.40);
INSERT INTO `ingredients` VALUES (5018, 'butter', 4.00);
INSERT INTO `ingredients` VALUES (5019, 'peas', 1.00);
INSERT INTO `ingredients` VALUES (5020, 'carrots', 0.50);
INSERT INTO `ingredients` VALUES (5021, 'beef', 6.00);
INSERT INTO `ingredients` VALUES (5022, 'pizza base', 4.00);
INSERT INTO `ingredients` VALUES (5023, 'tomato paste', 2.50);
INSERT INTO `ingredients` VALUES (5024, 'cheese', 5.00);
INSERT INTO `ingredients` VALUES (5025, 'salsa', 2.00);
INSERT INTO `ingredients` VALUES (5026, 'burger bun', 1.00);


--
-- Data for the 'ingredient_allergens' junction table
--

INSERT INTO `ingredient_allergens` VALUES (5001, 6004);
INSERT INTO `ingredient_allergens` VALUES (5001, 6013);

INSERT INTO `ingredient_allergens` VALUES (5002, 6001);
INSERT INTO `ingredient_allergens` VALUES (5002, 6003);
INSERT INTO `ingredient_allergens` VALUES (5002, 6013);

INSERT INTO `ingredient_allergens` VALUES (5003, 6013);

INSERT INTO `ingredient_allergens` VALUES (5007, 6005);

INSERT INTO `ingredient_allergens` VALUES (5009, 6013);

INSERT INTO `ingredient_allergens` VALUES (5010, 6003);
INSERT INTO `ingredient_allergens` VALUES (5010, 6010);

INSERT INTO `ingredient_allergens` VALUES (5012, 6013);

INSERT INTO `ingredient_allergens` VALUES (5015, 6003);
INSERT INTO `ingredient_allergens` VALUES (5015, 6010);

INSERT INTO `ingredient_allergens` VALUES (5026, 6011);
INSERT INTO `ingredient_allergens` VALUES (5026, 6013);




-- 
-- Data for the 'options' table
-- 

INSERT INTO `options` VALUES (3000, 'Fish and Chips', 2.00);
INSERT INTO `options` VALUES (3001, 'Pasta', 1.50);
INSERT INTO `options` VALUES (3002, 'Pizza', 1.80);
INSERT INTO `options` VALUES (3003, 'Curry', 2.00);
INSERT INTO `options` VALUES (3004, 'Roast Beef', 2.50);
INSERT INTO `options` VALUES (3005, 'Roast Chicken', 2.20);
INSERT INTO `options` VALUES (3006, 'Chicken Wrap', 0.80);
INSERT INTO `options` VALUES (3007, 'Burger', 1.00);
INSERT INTO `options` VALUES (3008, 'Salad', 1.00);
INSERT INTO `options` VALUES (3009, 'Pork Chop', 1.80);
INSERT INTO `options` VALUES (3010, 'Beans on Toast', 0.60);

--
-- Data for the 'option_ingredients' junction table
--

INSERT INTO `option_ingredients` VALUES (3000, 5000, 100);
INSERT INTO `option_ingredients` VALUES (3000, 5001, 250);

INSERT INTO `option_ingredients` VALUES (3001, 5002, 200);
INSERT INTO `option_ingredients` VALUES (3001, 5003, 150);
INSERT INTO `option_ingredients` VALUES (3001, 5004, 50);

INSERT INTO `option_ingredients` VALUES (3002, 5022, 100);
INSERT INTO `option_ingredients` VALUES (3002, 5023, 30);
INSERT INTO `option_ingredients` VALUES (3002, 5024, 30);

INSERT INTO `option_ingredients` VALUES (3003, 5005, 150);
INSERT INTO `option_ingredients` VALUES (3003, 5007, 200);
INSERT INTO `option_ingredients` VALUES (3003, 5008, 200);

INSERT INTO `option_ingredients` VALUES (3004, 5000, 200);
INSERT INTO `option_ingredients` VALUES (3004, 5019, 200);
INSERT INTO `option_ingredients` VALUES (3004, 5020, 100);
INSERT INTO `option_ingredients` VALUES (3004, 5021, 75);

INSERT INTO `option_ingredients` VALUES (3005, 5000, 200);
INSERT INTO `option_ingredients` VALUES (3005, 5005, 200);
INSERT INTO `option_ingredients` VALUES (3005, 5020, 100);
INSERT INTO `option_ingredients` VALUES (3005, 5006, 100);

INSERT INTO `option_ingredients` VALUES (3006, 5005, 100);
INSERT INTO `option_ingredients` VALUES (3006, 5009, 30);
INSERT INTO `option_ingredients` VALUES (3006, 5025, 10);

INSERT INTO `option_ingredients` VALUES (3007, 5013, 100);
INSERT INTO `option_ingredients` VALUES (3007, 5026, 20);

INSERT INTO `option_ingredients` VALUES (3008, 5004, 20);
INSERT INTO `option_ingredients` VALUES (3008, 5010, 25);
INSERT INTO `option_ingredients` VALUES (3008, 5011, 15);
INSERT INTO `option_ingredients` VALUES (3008, 5024, 10);

INSERT INTO `option_ingredients` VALUES (3009, 5000, 200);
INSERT INTO `option_ingredients` VALUES (3009, 5016, 200);
INSERT INTO `option_ingredients` VALUES (3009, 5019, 100);
INSERT INTO `option_ingredients` VALUES (3009, 5020, 100);

INSERT INTO `option_ingredients` VALUES (3010, 5012, 30);
INSERT INTO `option_ingredients` VALUES (3010, 5017, 80);
INSERT INTO `option_ingredients` VALUES (3010, 5018, 5);
