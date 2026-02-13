import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

async function main() {
  const today = new Date().toISOString().slice(0, 10);
  await prisma.menuDay.upsert({
    where: { date: today },
    create: {
      date: today,
      sourceUrl: "https://dining.berkeley.edu/menus/",
      menuItems: {
        create: [
          { name: "Scrambled Eggs", mealPeriod: "breakfast", calories: 180, protein: 14, carbs: 2, fat: 13 },
          { name: "Oatmeal", mealPeriod: "breakfast", calories: 150, protein: 5, carbs: 27, fat: 3 },
          { name: "Turkey Sausage", mealPeriod: "breakfast", calories: 110, protein: 9, carbs: 1, fat: 8 },
          { name: "Grilled Chicken", mealPeriod: "lunch", calories: 220, protein: 35, carbs: 0, fat: 8 },
          { name: "Mexican Rice", mealPeriod: "lunch", calories: 175, protein: 4, carbs: 35, fat: 2 },
          { name: "Black Beans", mealPeriod: "lunch", calories: 130, protein: 8, carbs: 23, fat: 1 },
          { name: "Salmon Fillet", mealPeriod: "dinner", calories: 280, protein: 25, carbs: 0, fat: 18 },
          { name: "Roasted Broccoli", mealPeriod: "dinner", calories: 55, protein: 4, carbs: 11, fat: 0 },
          { name: "Sweet Potato", mealPeriod: "dinner", calories: 100, protein: 1, carbs: 23, fat: 0 },
        ],
      },
    },
    update: {
      scrapedAt: new Date(),
      menuItems: {
        deleteMany: {},
        create: [
          { name: "Scrambled Eggs", mealPeriod: "breakfast", calories: 180, protein: 14, carbs: 2, fat: 13 },
          { name: "Oatmeal", mealPeriod: "breakfast", calories: 150, protein: 5, carbs: 27, fat: 3 },
          { name: "Turkey Sausage", mealPeriod: "breakfast", calories: 110, protein: 9, carbs: 1, fat: 8 },
          { name: "Grilled Chicken", mealPeriod: "lunch", calories: 220, protein: 35, carbs: 0, fat: 8 },
          { name: "Mexican Rice", mealPeriod: "lunch", calories: 175, protein: 4, carbs: 35, fat: 2 },
          { name: "Black Beans", mealPeriod: "lunch", calories: 130, protein: 8, carbs: 23, fat: 1 },
          { name: "Salmon Fillet", mealPeriod: "dinner", calories: 280, protein: 25, carbs: 0, fat: 18 },
          { name: "Roasted Broccoli", mealPeriod: "dinner", calories: 55, protein: 4, carbs: 11, fat: 0 },
          { name: "Sweet Potato", mealPeriod: "dinner", calories: 100, protein: 1, carbs: 23, fat: 0 },
        ],
      },
    },
  });
  console.log("Seed: menu for today created");
}

main()
  .then(() => prisma.$disconnect())
  .catch((e) => {
    console.error(e);
    prisma.$disconnect();
    process.exit(1);
  });
