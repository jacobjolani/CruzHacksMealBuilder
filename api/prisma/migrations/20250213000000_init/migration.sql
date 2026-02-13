-- CreateTable
CREATE TABLE "MenuDay" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "date" TEXT NOT NULL,
    "sourceUrl" TEXT,
    "scrapedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- CreateTable
CREATE TABLE "MenuItem" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "menuDayId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "mealPeriod" TEXT NOT NULL,
    "calories" REAL NOT NULL,
    "protein" REAL NOT NULL,
    "carbs" REAL NOT NULL,
    "fat" REAL NOT NULL,
    "tags" TEXT,
    CONSTRAINT "MenuItem_menuDayId_fkey" FOREIGN KEY ("menuDayId") REFERENCES "MenuDay" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "UserProfile" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sessionId" TEXT NOT NULL,
    "dailyCalories" REAL,
    "dailyProtein" REAL,
    "dailyCarbs" REAL,
    "dailyFat" REAL,
    "preferences" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL
);

-- CreateTable
CREATE TABLE "MealPlan" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "menuDayId" TEXT NOT NULL,
    "sessionId" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "totalsCalories" REAL NOT NULL,
    "totalsProtein" REAL NOT NULL,
    "totalsCarbs" REAL NOT NULL,
    "totalsFat" REAL NOT NULL,
    "meals" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "MenuDay_date_key" ON "MenuDay"("date");

-- CreateIndex
CREATE UNIQUE INDEX "UserProfile_sessionId_key" ON "UserProfile"("sessionId");
