from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.users import Student, UserRole
from app.db.db_session import get_session

async def create_test_student(full_name: str, group_id: int = None, kodstud: int = None, id_stud: int = None):
    """Creates a test student in the database."""
    async with get_session() as db_session:
        try:
            student = Student(
                full_name=full_name,
                role=UserRole.STUDENT,
                group_id=group_id,
                kodstud=kodstud,
                id_stud=id_stud,
            )
            db_session.add(student)
            await db_session.commit()
            print(f"Test student '{full_name}' created successfully.")
        except Exception as e:
            await db_session.rollback()
            print(f"Error creating test student: {e}")
            
async def delete_test_student(student_id: int):  # Corrected function signature
    """Deletes a test student from the database."""
    async with get_session() as db_session:
        try:
            # Get the student by ID
            stmt = select(Student).where(Student.id == student_id)
            result = await db_session.execute(stmt)
            student = result.scalar_one_or_none()

            if student:
                await db_session.delete(student)  # Delete the student
                await db_session.commit()
                print(f"Test student with ID '{student_id}' deleted successfully.")
            else:
                print(f"Test student with ID '{student_id}' not found.")

        except Exception as e:
            await db_session.rollback()
            print(f"Error deleting test student: {e}")
