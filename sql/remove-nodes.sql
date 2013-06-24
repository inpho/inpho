
 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO';
INSERT INTO inphonodes.entity (ID, label, typeID, oldID, searchstring)
     VALUES (0, 'philosophy', 1, 0, 'philosophy');
INSERT INTO inphonodes.idea (ID, label, searchpattern, pattern_type)
     VALUES (0, 'philosophy', '(\bphilosophy\b)|(\bphilosophies\b)', 1);

ALTER TABLE `inphonodes`.`idea_instance_of` ADD COLUMN `backbone` BIT(1) NOT NULL DEFAULT 0  AFTER `class_id` ;

INSERT INTO idea_instance_of (class_id, instance_id, backbone)
SELECT parent.id as class_id, concept.id as instance_id, 1 as backbone
FROM idea parent, idea concept, ontotree node, ontotree parent_node
WHERE node.concept_id = concept.ID
  AND node.parent_id = parent_node.ID
  AND parent_node.concept_id = parent.ID;

INSERT INTO idea_instance_of (class_id, instance_id, backbone)
SELECT 0 as class_id, concept.id as instance_id, 1 as backbone
FROM idea concept, ontotree node
WHERE node.concept_id = concept.ID
  AND node.parent_id IS NULL;

DROP TABLE ontotree;

DELETE FROM entity
WHERE entity.typeID = 2;

SET SQL_MODE=@OLD_SQL_MODE;
