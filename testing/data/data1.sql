
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `table1`;
DROP TABLE IF EXISTS `table2`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `table1` (
    `field1` int(10),
    `field2` char(10),
    PRIMARY KEY (`field1`)
);

CREATE TABLE `table2` (
    `field1` int(10),
    `field2` int(10),
    `field3` char(10),
    PRIMARY KEY (`field1`),
    FOREIGN KEY (`field2`) REFERENCES `table1`(`field1`)
);

INSERT INTO `table1` VALUES (1, "a");
INSERT INTO `table1` VALUES (2, "b");
INSERT INTO `table1` VALUES (3, "c");

INSERT INTO `table2` VALUES (1, 3, "x");
INSERT INTO `table2` VALUES (2, 2, "y");
INSERT INTO `table2` VALUES (3, 1, "z");
