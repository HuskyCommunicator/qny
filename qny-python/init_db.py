from database import engine, Base
from models import User, Agent, ChatMessage, ChatSession
import bcrypt

def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

def create_default_data():
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 创建默认用户
        if not session.query(User).filter(User.username == "admin").first():
            hashed_password = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=hashed_password.decode('utf-8'),
                is_active=True
            )
            session.add(admin_user)
            print("Created default admin user")

        # 创建默认AI角色
        default_agents = [
            {
                "name": "哈利波特",
                "description": "来自霍格沃茨的勇敢巫师",
                "system_prompt": "You are Harry Potter, a brave wizard from Hogwarts. You are friendly, courageous, and always willing to help others. You speak with a British accent and often mention magic and wizarding world concepts.",
                "category": "fiction",
                "is_public": True
            },
            {
                "name": "苏格拉底",
                "description": "古希腊哲学家，以提问方式教学",
                "system_prompt": "You are Socrates, a philosopher who answers in questions. You believe in the Socratic method of teaching through questioning. You are wise, patient, and always seek truth through dialogue.",
                "category": "philosophy",
                "is_public": True
            },
            {
                "name": "夏洛克·福尔摩斯",
                "description": "著名的侦探大师",
                "system_prompt": "You are Sherlock Holmes, the master detective. You are highly intelligent, observant, and analytical. You often notice details that others miss and you solve mysteries through logical reasoning.",
                "category": "fiction",
                "is_public": True
            }
        ]

        for agent_data in default_agents:
            if not session.query(Agent).filter(Agent.name == agent_data["name"]).first():
                agent = Agent(**agent_data)
                session.add(agent)
                print(f"Created default agent: {agent_data['name']}")

        session.commit()
        print("Default data created successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error creating default data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    create_tables()
    create_default_data()