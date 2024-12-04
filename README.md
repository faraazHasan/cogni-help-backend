<!-- Note : Do not create, update, alter or delete anything from database structure manually, use alembic here -->

<!-- Command to run backend server -->

run server - uvicorn app.main:app --reload

<!-- Alembic commands -->

<!-- After changes done in modal run below command to create alembic file -->
<!-- Note: "enter_alembic_version_file_name" should specify its work like, "create users table" to create a new table named users -->

alembic revision --autogenerate -m "<enter_alembic_version_file_name>"

<!-- Once file generates we are ready for database migration. -->
<!-- add alembic code in the generated file -->
<!-- Once you run the below command your tables will be generated in your database. -->

alembic upgrade head

<!-- Command to run pre-commit manually -->

pre-commit run --all-files
