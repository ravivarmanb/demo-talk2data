from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime, timedelta
import random
from faker import Faker
import os

Base = declarative_base()

class Address(Base):
    __tablename__ = 'addresses'
    address_id = Column(Integer, primary_key=True)
    street_address = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default='USA')

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    email = Column(String(200))
    phone = Column(String(20))
    ssn = Column(String(11))
    address_id = Column(Integer, ForeignKey('addresses.address_id'))
    
    address = relationship("Address")
    policies = relationship("Policy", back_populates="customer")
    claims = relationship("Claim", back_populates="customer")

class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200))
    phone = Column(String(20))
    hire_date = Column(Date)
    address_id = Column(Integer, ForeignKey('addresses.address_id'))
    
    address = relationship("Address")
    policies = relationship("Policy", back_populates="agent")

class PolicyType(Base):
    __tablename__ = 'policy_types'
    type_id = Column(Integer, primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    base_premium = Column(Float)
    coverage_limit = Column(Float)
    
    policies = relationship("Policy", back_populates="policy_type")

class Policy(Base):
    __tablename__ = 'policies'
    policy_id = Column(Integer, primary_key=True)
    policy_number = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    agent_id = Column(Integer, ForeignKey('agents.agent_id'))
    type_id = Column(Integer, ForeignKey('policy_types.type_id'))
    start_date = Column(Date)
    end_date = Column(Date)
    premium = Column(Float)
    status = Column(String(20))  # Active, Expired, Cancelled
    
    customer = relationship("Customer", back_populates="policies")
    agent = relationship("Agent", back_populates="policies")
    policy_type = relationship("PolicyType", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")

class Claim(Base):
    __tablename__ = 'claims'
    claim_id = Column(Integer, primary_key=True)
    claim_number = Column(String(50), unique=True)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'))
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    claim_date = Column(DateTime)
    description = Column(Text)
    amount_claimed = Column(Float)
    amount_paid = Column(Float)
    status = Column(String(20))  # Pending, Approved, Denied, Paid
    
    policy = relationship("Policy", back_populates="claims")
    customer = relationship("Customer", back_populates="claims")

class Prospect(Base):
    __tablename__ = 'prospects'
    prospect_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(200))
    phone = Column(String(20))
    source = Column(String(100))  # Web, Referral, Advertisement, etc.
    status = Column(String(50))   # New, Contacted, Converted, Not Interested
    notes = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self, db_path='sqlite:///health_insurance.db'):
        self.engine = create_engine(db_path)
        self.Session = sessionmaker(bind=self.engine)
        
    def init_db(self):
        Base.metadata.create_all(self.engine)
        
    def drop_tables(self):
        Base.metadata.drop_all(self.engine)
        
    def create_sample_data(self, num_records=50):
        fake = Faker()
        session = self.Session()
        
        try:
            # Create policy types
            policy_types = [
                PolicyType(
                    name="Basic Health",
                    description="Basic health insurance coverage",
                    base_premium=200.0,
                    coverage_limit=100000.0
                ),
                PolicyType(
                    name="Family Plan",
                    description="Health insurance for the whole family",
                    base_premium=500.0,
                    coverage_limit=500000.0
                ),
                PolicyType(
                    name="Senior Care",
                    description="Comprehensive coverage for seniors",
                    base_premium=350.0,
                    coverage_limit=300000.0
                ),
                PolicyType(
                    name="Student Health",
                    description="Affordable coverage for students",
                    base_premium=150.0,
                    coverage_limit=100000.0
                )
            ]
            session.add_all(policy_types)
            
            # Create addresses
            addresses = []
            for _ in range(num_records):
                address = Address(
                    street_address=fake.street_address(),
                    city=fake.city(),
                    state=fake.state_abbr(),
                    zip_code=fake.zipcode(),
                    country='USA'
                )
                addresses.append(address)
            session.add_all(addresses)
            
            # Create agents
            agents = []
            for i in range(5):
                agent = Agent(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    hire_date=fake.date_between(start_date='-5y', end_date='today'),
                    address=addresses[i]
                )
                agents.append(agent)
            session.add_all(agents)
            
            # Create customers and policies
            customers = []
            for i in range(5, num_records):
                customer = Customer(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    ssn=fake.ssn(),
                    address=addresses[i]
                )
                customers.append(customer)
                
                # Each customer gets 1-3 policies
                for _ in range(random.randint(1, 3)):
                    policy_type = random.choice(policy_types)
                    start_date = fake.date_between(start_date='-2y', end_date='today')
                    policy = Policy(
                        policy_number=f"POL-{fake.unique.random_number(digits=8)}",
                        customer=customer,
                        agent=random.choice(agents),
                        policy_type=policy_type,
                        start_date=start_date,
                        end_date=start_date + timedelta(days=365),
                        premium=policy_type.base_premium * (0.8 + random.random() * 0.4),  # Randomize premium slightly
                        status=random.choices(['Active', 'Expired', 'Cancelled'], weights=[0.8, 0.15, 0.05])[0]
                    )
                    session.add(policy)
                    
                    # Add claims for some policies
                    if random.random() > 0.7:  # 30% chance of having claims
                        for _ in range(random.randint(1, 4)):
                            claim_date = fake.date_time_between(start_date=start_date, end_date='now')
                            amount_claimed = random.uniform(100, policy_type.coverage_limit * 0.1)
                            claim = Claim(
                                claim_number=f"CLM-{fake.unique.random_number(digits=8)}",
                                policy=policy,
                                customer=customer,
                                claim_date=claim_date,
                                description=fake.sentence(),
                                amount_claimed=amount_claimed,
                                amount_paid=amount_claimed * random.uniform(0.7, 1.0),
                                status=random.choices(['Pending', 'Approved', 'Denied', 'Paid'], 
                                                    weights=[0.2, 0.3, 0.1, 0.4])[0]
                            )
                            session.add(claim)
            
            # Create some prospects
            for _ in range(20):
                prospect = Prospect(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    phone=fake.phone_number(),
                    source=random.choice(['Web', 'Referral', 'Advertisement', 'Cold Call', 'Email Campaign']),
                    status=random.choice(['New', 'Contacted', 'Converted', 'Not Interested']),
                    notes=fake.paragraph()
                )
                session.add(prospect)
            
            session.commit()
            print(f"Created {len(customers)} customers, {len(agents)} agents, and related records.")
            
        except Exception as e:
            session.rollback()
            print(f"Error creating sample data: {e}")
            raise
        finally:
            session.close()

if __name__ == "__main__":
    db = Database()
    db.drop_tables()
    db.init_db()
    db.create_sample_data(50)
    print("Database initialized with sample data.")
