from datetime import datetime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy import (CheckConstraint,UniqueConstraint,ForeignKey,Table,Column,Integer,String,DateTime,)
from sqlalchemy.ext.declarative import declarative_base
import prettytable
from sqlalchemy.exc import IntegrityError

engine = create_engine('sqlite:///law_firm.db')
Session = sessionmaker(bind=engine)
Base = declarative_base()

lawyer_client = Table(
    'lawyer_client',
    Base.metadata,
    Column('lawyer_id', ForeignKey('lawyers.id'), primary_key=True),
    Column('client_id', ForeignKey('clients.id'), primary_key=True),
    extend_existing=True,
)

class Lawyer(Base):
    __tablename__ = 'lawyers'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    email = Column(String())

    meetings = relationship('Meeting', backref='lawyer')
    clients = relationship('Client', secondary='lawyer_client', back_populates='lawyers')

    def __repr__(self):
        return f'Lawyer(id={self.id}, ' + \
            f'name={self.name}, ' + \
            f'email={self.email})'


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer(), primary_key=True)
    name = Column(String())
    email = Column(String())

    lawyers = relationship('Lawyer', secondary=lawyer_client, back_populates='clients')
    meetings = relationship('Meeting', backref=('client'))

    def __repr__(self):
        return f'Client(id={self.id}, ' + \
            f'name={self.name})'

class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer(), primary_key=True)

    meeting_note = Column(String())
    created_at = Column(DateTime(), server_default=func.now())
    updated_at = Column(DateTime(), onupdate=func.now())

    lawyer_id = Column(Integer(), ForeignKey('lawyers.id'))
    client_id = Column(Integer(), ForeignKey('clients.id'))

    def __repr__(self):
        return f'Meeting(id={self.id}, ' + \
            f'meeting_note={self.meeting_note}, ' + \
            f'created_at={self.created_at}, ' + \
            f'updated_at={self.updated_at})'

Base.metadata.create_all(engine)

def view_lawyers(session):
    lawyers = session.query(Lawyer).all()
    lawyers_table = prettytable.PrettyTable()
    lawyers_table.field_names = ["ID", "Name", "Email"]
    for lawyer in lawyers:
        lawyers_table.add_row([lawyer.id, lawyer.name, lawyer.email])
    print("Lawyers:")
    print(lawyers_table)

def view_clients(session):
    clients = session.query(Client).all()
    clients_table = prettytable.PrettyTable()
    clients_table.field_names = ["ID", "Name"]
    for client in clients:
        clients_table.add_row([client.id, client.name])
    print("Clients:")
    print(clients_table)

def view_meetings(session):
    meetings = session.query(Meeting).all()
    meetings_table = prettytable.PrettyTable()
    meetings_table.field_names = ["ID", "Meeting Note", "Created At", "Updated At", "Lawyer", "Client"]
    for meeting in meetings:
        lawyer_name = meeting.lawyer.name if meeting.lawyer else "N/A"
        client_name = meeting.client.name if meeting.client else "N/A"
        meetings_table.add_row([meeting.id, meeting.meeting_note, meeting.created_at, meeting.updated_at, lawyer_name, client_name])
    print("Meetings:")
    print(meetings_table)


def add_lawyer(session):
    name = input("Enter lawyer's name: ")
    email = input("Enter lawyer's email: ")
    lawyer = Lawyer(name=name, email=email)
    session.add(lawyer)
    try:
        session.commit()
        print("Lawyer added successfully.")
    except IntegrityError as e:
        session.rollback()
        print(f"Error: {e}")
        print("Failed to add lawyer. Please check if the email is unique.")

def add_client(session):
    name = input("Enter client's name: ")
    email = input("Enter client's email: ")
    client = Client(name=name, email=email)
    session.add(client)
    try:
        session.commit()
        print("Client added successfully.")
    except IntegrityError as e:
        session.rollback()
        print(f"Error: {e}")
        print("Failed to add client. Please check if the email is unique.")

def delete_lawyer(session):
    lawyer_id = input("Enter lawyer's ID to delete: ")
    lawyer = session.query(Lawyer).filter_by(id=lawyer_id).first()
    if lawyer:
        session.delete(lawyer)
        session.commit()
        print(f"Lawyer with ID {lawyer_id} deleted successfully.")
    else:
        print(f"Lawyer with ID {lawyer_id} not found.")

def delete_client(session):
    client_id = input("Enter client's ID to delete: ")
    client = session.query(Client).filter_by(id=client_id).first()
    if client:
        session.delete(client)
        session.commit()
        print(f"Client with ID {client_id} deleted successfully.")
    else:
        print(f"Client with ID {client_id} not found.")

def update_lawyer_email(session):
    lawyer_id = input("Enter lawyer's ID to update email: ")
    new_email = input("Enter the new email: ")
    lawyer = session.query(Lawyer).filter_by(id=lawyer_id).first()
    if lawyer:
        lawyer.email = new_email
        session.commit()
        print(f"Email for Lawyer with ID {lawyer_id} updated successfully.")
    else:
        print(f"Lawyer with ID {lawyer_id} not found.")

def update_client_email(session):
    client_id = input("Enter client's ID to update email: ")
    new_email = input("Enter the new email: ")
    client = session.query(Client).filter_by(id=client_id).first()
    if client:
        client.email = new_email
        session.commit()
        print(f"Email for Client with ID {client_id} updated successfully.")
    else:
        print(f"Client with ID {client_id} not found.")
def delete_meeting(session):
    meeting_id = input("Enter meeting's ID to delete: ")
    meeting = session.query(Meeting).filter_by(id=meeting_id).first()
    if meeting:
        session.delete(meeting)
        session.commit()
        print(f"Meeting with ID {meeting_id} deleted successfully.")
    else:
        print(f"Meeting with ID {meeting_id} not found.")
def add_meeting(session):
    meeting_note = input("Enter meeting note: ")
    lawyer_id = input("Enter lawyer's ID: ")
    client_id = input("Enter client's ID: ")

    lawyer = session.query(Lawyer).filter_by(id=lawyer_id).first()
    client = session.query(Client).filter_by(id=client_id).first()

    if lawyer and client:
        meeting = Meeting(meeting_note=meeting_note, lawyer_id=lawyer_id, client_id=client_id)
        session.add(meeting)
        session.commit()
        print("Meeting added successfully.")
    else:
        print("Lawyer or client not found. Please check the provided IDs.")
while True:
    print("\nMain Menu:")
    print("1. Add Lawyer")
    print("2. Add Client")
    print("3. Add Meeting")
    print("4. Delete Lawyer")
    print("5. Delete Client")
    print("6. Delete Meeting")
    print("7. Update Lawyer Email")
    print("8. Update Client Email")
    print("9. View Lawyers")
    print("10. View Clients")
    print("11. View Meetings")
    print("12. Exit")

    choice = input("Enter your choice: ")

    session = Session()

    if choice == "1":
        add_lawyer(session)
    elif choice == "2":
        add_client(session)
    elif choice == "3":
        add_meeting(session)
    elif choice == "4":
        delete_lawyer(session)
    elif choice == "5":
        delete_client(session)
    elif choice == "6":
        delete_meeting(session)
    elif choice == "7":
        update_lawyer_email(session)
    elif choice == "8":
        update_client_email(session)
    elif choice == "9":
        view_lawyers(session)
    elif choice == "10":
        view_clients(session)
    elif choice == "11":
        view_meetings(session)
    elif choice == "12":
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Please try again.")
