CREATE TABLE destroyed_problems (
    destroyedProblemID INT PRIMARY KEY NOT NULL ,
    domainFilePath TEXT NOT NULL,
    problemFilePath TEXT NOT NULL
);

CREATE TABLE added_preconditions (
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    PRIMARY KEY (destroyedProblemID, action_name, fluent_name)
);

create TABLE modifiers(
    modifierVersionID INT PRIMARY KEY NOT NULL,
    modifierName TEXT NOT NULL
);

INSERT INTO modifiers (modifierVersionID, modifierName)
VALUES 
(1, "ExpModifier"),
(2, "LinModifier");

CREATE TABLE results (
    resultID INT PRIMARY KEY NOT NULL,
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    FOREIGN KEY (modifierVersionID) REFERENCES modifiers(modifierVersionID),
    timeInMilliseconds INT NOT NULL
);

CREATE TABLE left_preconditions_results(
    FOREIGN KEY (resultID) REFERENCES results(resultID),
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    PRIMARY KEY (resultID, actionName, fluentName)
)