CREATE TABLE original_problems (
    originalProblemID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    domainFilePath TEXT NOT NULL,
    problemFilePath TEXT NOT NULL,
    planSolvableCost INT NOT NULL,
    timeInMilliseconds INTEGER NOT NULL,
    errorText TEXT,
    longerThan30Minutes INTEGER
);

CREATE TABLE destroyed_problems (
    destroyedProblemID INTEGER PRIMARY KEY NOT NULL,
    domainFilePath TEXT NOT NULL,
    problemFilePath TEXT NOT NULL,
    domainContent TEXT NOT NULL,
    problemContent TEXT NOT NULL,
    errorText TEXT
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