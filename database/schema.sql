PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Users (
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    FullName TEXT NOT NULL,
    Email TEXT NOT NULL UNIQUE,
    PasswordHash TEXT,
    GoogleId TEXT,
    Role TEXT NOT NULL DEFAULT 'user'
        CHECK (Role IN ('user', 'admin')),
    IsActive INTEGER NOT NULL DEFAULT 1,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    LastLoginAt TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS UX_Users_GoogleId
ON Users(GoogleId)
WHERE GoogleId IS NOT NULL;


CREATE TABLE IF NOT EXISTS Conversations (
    ConvId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    Sender TEXT NOT NULL
        CHECK (Sender IN ('user', 'bot')),
    Message TEXT NOT NULL,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_Conv_User
ON Conversations(UserId, CreatedAt DESC);


CREATE TABLE IF NOT EXISTS Medications (
    MedId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    DrugName TEXT NOT NULL,
    Dosage TEXT,
    TimesPerDay INTEGER NOT NULL DEFAULT 1,
    StartDate TEXT NOT NULL,
    EndDate TEXT,
    Note TEXT,
    IsActive INTEGER NOT NULL DEFAULT 1,

    FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MedicationTimes (
    TimeId INTEGER PRIMARY KEY AUTOINCREMENT,
    MedId INTEGER NOT NULL,
    TakeTime TEXT NOT NULL,

    FOREIGN KEY (MedId)
        REFERENCES Medications(MedId)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS MedicationLogs (
    LogId INTEGER PRIMARY KEY AUTOINCREMENT,
    MedId INTEGER NOT NULL,
    ScheduledAt TEXT NOT NULL,
    Status TEXT NOT NULL DEFAULT 'pending'
        CHECK (Status IN ('pending','taken','missed','snoozed')),
    ActionAt TEXT,

    FOREIGN KEY (MedId)
        REFERENCES Medications(MedId)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Appointments (
    ApptId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    DoctorName TEXT NOT NULL,
    Location TEXT,
    ApptTime TEXT NOT NULL,
    Content TEXT,
    Note TEXT,
    Status TEXT NOT NULL DEFAULT 'upcoming'
        CHECK (Status IN ('upcoming','done','cancelled','missed')),
    RemindBefore INTEGER NOT NULL DEFAULT 1440
        CHECK (RemindBefore IN (60,180,1440,2880,10080)),
    Channel TEXT NOT NULL DEFAULT 'web'
        CHECK (Channel = 'web'),
    ConfirmedAt TEXT,
    ReminderCount INTEGER NOT NULL DEFAULT 0,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_Appt_User
ON Appointments(UserId, ApptTime);


CREATE TABLE IF NOT EXISTS Symptoms (
    SymptomId INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE
);


CREATE TABLE IF NOT EXISTS Conditions (
    ConditionId INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL UNIQUE,
    Recommendation TEXT,
    IsSerious INTEGER NOT NULL DEFAULT 0
);


CREATE TABLE IF NOT EXISTS ConditionSymptoms (
    ConditionId INTEGER NOT NULL,
    SymptomId INTEGER NOT NULL,
    Weight REAL NOT NULL DEFAULT 1.0,

    PRIMARY KEY (ConditionId, SymptomId),

    FOREIGN KEY (ConditionId)
        REFERENCES Conditions(ConditionId)
        ON DELETE CASCADE,

    FOREIGN KEY (SymptomId)
        REFERENCES Symptoms(SymptomId)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS SymptomChecks (
    CheckId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,
    SymptomText TEXT NOT NULL,
    Severity INTEGER NOT NULL
        CHECK (Severity BETWEEN 1 AND 3),
    DaysSince INTEGER,
    ResultJson TEXT,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS Notifications (
    NotificationId INTEGER PRIMARY KEY AUTOINCREMENT,
    UserId INTEGER NOT NULL,

    Title TEXT NOT NULL,
    Message TEXT NOT NULL,

    NotificationType TEXT NOT NULL DEFAULT 'appointment',

    SentAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    Status TEXT NOT NULL DEFAULT 'unread'
        CHECK (Status IN ('unread','read')),

    FOREIGN KEY (UserId)
        REFERENCES Users(UserId)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS IX_Notifications_User
ON Notifications(UserId, SentAt DESC);