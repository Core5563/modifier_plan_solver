CREATE TABLE destroyed_problems (
    destroyedProblemID INT PRIMARY KEY NOT NULL ,
    domainFilePath TEXT NOT NULL,
    problemFilePath TEXT NOT NULL
);

CREATE TABLE added_preconditions (
    destroyedProblemID INT NOT NULL,
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    PRIMARY KEY (destroyedProblemID, actionName, fluentName)
);

create TABLE modifiers(
    modifierVersionID INT NOT NULL PRIMARY KEY,
    modifierName TEXT NOT NULL
);

INSERT INTO modifiers (modifierVersionID, modifierName)
VALUES 
(1, "ExpModifier"),
(2, "LinModifier");

CREATE TABLE results (
    resultID INT PRIMARY KEY NOT NULL,
    destroyedProblemID INT NOT NULL,
    modifierVersionID INT NOT NULL,
    timeInMilliseconds INT NOT NULL,
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    FOREIGN KEY (modifierVersionID) REFERENCES modifiers(modifierVersionID)
);

CREATE TABLE left_preconditions_results(
    resultID INT NOT NULL,
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    FOREIGN KEY (resultID) REFERENCES results(resultID),
    PRIMARY KEY (resultID, actionName, fluentName)
)