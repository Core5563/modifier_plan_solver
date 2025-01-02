CREATE TABLE destroyed_problems (
    destroyedProblemID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    domainFilePath TEXT NOT NULL,
    problemFilePath TEXT NOT NULL,
    originalDomainFilePath TEXT NOT NULL,
    originalProblemFilePath TEXT NOT NULL
);

CREATE TABLE added_preconditions (
    destroyedProblemID INTEGER NOT NULL,
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    PRIMARY KEY (destroyedProblemID, actionName, fluentName)
);

create TABLE modifiers(
    modifierVersionID INTEGER NOT NULL PRIMARY KEY,
    modifierName TEXT NOT NULL
);

INSERT INTO modifiers (modifierVersionID, modifierName)
VALUES 
(1, "ExpModifier"),
(2, "LinModifier");

CREATE TABLE results (
    resultID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    destroyedProblemID INTEGER NOT NULL,
    modifierVersionID INTEGER NOT NULL,
    timeInMilliseconds INTEGER NOT NULL,
    FOREIGN KEY (destroyedProblemID) REFERENCES destroyed_problems(destroyedProblemID),
    FOREIGN KEY (modifierVersionID) REFERENCES modifiers(modifierVersionID)
);

CREATE TABLE left_preconditions_results(
    resultID INTEGER NOT NULL,
    actionName TEXT NOT NULL,
    fluentName TEXT NOT NULL,
    FOREIGN KEY (resultID) REFERENCES results(resultID),
    PRIMARY KEY (resultID, actionName, fluentName)
)