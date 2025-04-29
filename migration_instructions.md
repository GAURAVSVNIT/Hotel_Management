# Database Migration Instructions

Follow these steps to create and apply the migration for the new `has_been_reviewed` field in the Order model:

## Step 1: Create the migration file

Navigate to your project's root directory in your terminal/command prompt:

```
cd D:\Coding\VSCODE\Hotel_Management
```

Then run the makemigrations command:

```
python manage.py makemigrations main
```

This will create a new migration file in the `main/migrations/` directory that adds the `has_been_reviewed` field to the Order model.

## Step 2: Apply the migration

Now apply the migration to update the database schema:

```
python manage.py migrate main
```

This will add the new column to the `main_order` table in your database.

## Verifying the migration

You can verify that the migration was successful by checking the database schema or by running:

```
python manage.py showmigrations main
```

This should show that all migrations for the `main` app have been applied, including the newly created one.

## Troubleshooting

If you encounter any issues:

1. Make sure you're running the commands from the project root directory (where manage.py is located)
2. If you get errors related to existing data, you may need to provide a default value for the new field
3. If you've already made other changes to models, those will be included in the migration as well

