from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import Course
import random

class Command(BaseCommand):
    help = 'Populate the database with realistic tech courses'

    def handle(self, *args, **options):
        # Check if courses already exist to avoid duplicates
        if Course.objects.exists():
            self.stdout.write(
                self.style.WARNING('Courses already exist in database. Skipping population.')
            )
            return

        # Create some instructor users if they don't exist
        instructor_names = [
            'Alex Johnson', 'Maria Garcia', 'David Chen', 'Sarah Williams',
            'Robert Kim', 'Jennifer Davis', 'Michael Brown', 'Laura Miller',
            'James Wilson', 'Emily Taylor', 'Daniel Anderson', 'Olivia Thomas'
        ]
        
        instructors = []
        for name in instructor_names:
            # Split name into first and last for username generation
            first_name, last_name = name.split(' ', 1)
            username = f"{first_name.lower()}_{last_name.lower()}"
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': f"{username}@learnify.com",
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                user.set_password('instructor123')  # Default password
                user.save()
            instructors.append(user)

        # Course data: (title, category, level, duration, summary, description, price)
        courses_data = [
            # Full-Stack Web Development
            ('React.js Complete Guide: Build Modern Web Apps', 'Full-Stack Web Development', 'Beginner', '12 hours', 
             'Learn React from scratch to building production-ready applications', 
             'Master React.js with hooks, context API, routing, and state management. Build 3 real-world projects including an e-commerce site, social media dashboard, and productivity app.', 
             89.99),
            
            ('Full-Stack Development with Node.js and MongoDB', 'Full-Stack Web Development', 'Intermediate', '18 hours',
             'Build scalable REST APIs and connect them with modern frontend frameworks',
             'Learn to build robust backends with Node.js, Express, and MongoDB. Implement authentication, file uploads, testing, and deployment strategies. Connect with React/Vue frontends.',
             99.99),
            
            ('Vue 3 Masterclass: Composition API and Vuex', 'Full-Stack Web Development', 'Intermediate', '15 hours',
             'Deep dive into Vue 3s reactivity system and state management patterns',
             'Explore the Composition API, Vuex 4, and Vue Router 4. Build enterprise-grade applications with TypeScript integration and testing strategies.',
             79.99),
            
            ('Angular Enterprise Application Development', 'Full-Stack Web Development', 'Advanced', '22 hours',
             'Architect and build large-scale Angular applications with best practices',
             'Learn Angular CLI, RxJS, state management with NgRx, and advanced component patterns. Implement authentication, lazy loading, and performance optimization.',
             119.99),
            
            ('Progressive Web Apps (PWA) with Service Workers', 'Full-Stack Web Development', 'Intermediate', '8 hours',
             'Create offline-capable web applications that feel native',
             'Learn to implement service workers, caching strategies, push notifications, and app manifest files. Convert existing web apps to PWAs and deploy to various platforms.',
             69.99),
            
            # Artificial Intelligence & Machine Learning
            ('Machine Learning Foundations: From Linear Regression to Neural Networks', 'Artificial Intelligence & Machine Learning', 'Beginner', '20 hours',
             'Understand core ML algorithms and implement them from scratch',
             'Start with linear regression and progress through decision trees, SVM, k-means clustering, and neural networks. Use Python with NumPy and matplotlib for implementations.',
             89.99),
            
            ('Deep Learning with TensorFlow 2 and Keras', 'Artificial Intelligence & Machine Learning', 'Intermediate', '25 hours',
             'Build and deploy neural networks for computer vision and NLP',
             'Master convolutional networks for image classification, recurrent networks for sequence data, and transformer architectures. Deploy models using TensorFlow Serving.',
             109.99),
            
            ('Natural Language Processing with Transformers', 'Artificial Intelligence & Machine Learning', 'Advanced', '18 hours',
             'Work with state-of-the-art language models like BERT and GPT',
             'Learn tokenization, embedding techniques, fine-tuning pre-trained models, and building applications like sentiment analysis, chatbots, and translation systems.',
             129.99),
            
            ('Computer Vision Applications with OpenCV and Deep Learning', 'Artificial Intelligence & Machine Learning', 'Intermediate', '16 hours',
             'Process and analyze visual data using traditional and deep learning methods',
             'Build face detection systems, object tracking, image segmentation, and optical character recognition applications. Combine OpenCV with deep learning frameworks.',
             94.99),
            
            ('MLOps: Deploying Machine Learning Models at Scale', 'Artificial Intelligence & Machine Learning', 'Advanced', '14 hours',
             'Learn to productionize ML models with monitoring and scaling',
             'Cover model versioning, A/B testing, containerization with Docker, Kubernetes orchestration, and CI/CD pipelines for machine learning workflows.',
             139.99),
            
            # Cybersecurity & Ethical Hacking
            ('Ethical Hacking: Penetration Testing and Vulnerability Assessment', 'Cybersecurity & Ethical Hacking', 'Beginner', '24 hours',
             'Learn to think like a hacker to defend systems effectively',
             'Master reconnaissance, scanning, exploitation, and post-exploitation techniques. Use Kali Linux, Metasploit, Burp Suite, and Wireshark in hands-on labs.',
             119.99),
            
            ('Network Security Fundamentals and Firewall Configuration', 'Cybersecurity & Ethical Hacking', 'Beginner', '15 hours',
             'Protect network infrastructure from common threats and attacks',
             'Study TCP/IP fundamentals, firewall rules, IDS/IPS systems, VPN technologies, and wireless security protocols. Implement defense-in-depth strategies.',
             89.99),
            
            ('Web Application Security: OWASP Top 10 and Secure Coding', 'Cybersecurity & Ethical Hacking', 'Intermediate', '20 hours',
             'Identify and fix security vulnerabilities in web applications',
             'Learn about injection attacks, broken authentication, sensitive data exposure, and XXE. Implement secure coding practices and use security testing tools.',
             99.99),
            
            ('Cryptography and Blockchain Security Fundamentals', 'Cybersecurity & Ethical Hacking', 'Advanced', '18 hours',
             'Understand modern cryptographic techniques and their applications',
             'Study symmetric/asymmetric encryption, hashing, digital signatures, zero-knowledge proofs, and secure multi-party computation. Apply to blockchain and cryptocurrencies.',
             129.99),
            
            ('Incident Response and Digital Forensics', 'Cybersecurity & Ethical Hacking', 'Intermediate', '22 hours',
             'Detect, respond to, and investigate security breaches',
             'Learn evidence collection, malware analysis, memory forensics, network forensics, and legal aspects of cyber investigations. Use industry-standard tools.',
             109.99),
            
            # Cloud Computing (AWS/Google Cloud)
            ('AWS Certified Solutions Architect Associate Complete Course', 'Cloud Computing (AWS/Google Cloud)', 'Beginner', '30 hours',
             'Prepare for AWS SAA-C03 certification with hands-on labs',
             'Master EC2, S3, VPC, RDS, Lambda, and CloudFormation. Design highly available, fault-tolerant, and cost-effective systems on AWS.',
             149.99),
            
            ('Google Cloud Professional Cloud Architect Certification', 'Cloud Computing (AWS/Google Cloud)', 'Beginner', '28 hours',
             'Prepare for Google Cloud PCA certification with practical exercises',
             'Learn Compute Engine, Cloud Storage, VPC, BigQuery, Kubernetes Engine, and Deployment Manager. Design scalable and secure cloud solutions.',
             149.99),
            
            ('Serverless Architecture with AWS Lambda and API Gateway', 'Cloud Computing (AWS/Google Cloud)', 'Intermediate', '16 hours',
             'Build event-driven applications without managing servers',
             'Create REST APIs with Lambda and API Gateway, implement event-driven architectures with SNS/SQS, and monitor with CloudWatch. Implement CI/CD for serverless apps.',
             119.99),
            
            ('Kubernetes Deep Dive: Orchestration at Scale', 'Cloud Computing (AWS/Google Cloud)', 'Advanced', '24 hours',
             'Master container orchestration with Kubernetes for production workloads',
             'Learn pod networking, storage, security, Helm charts, operators, and GitOps workflows. Troubleshoot clusters and implement monitoring with Prometheus.',
             139.99),
            
            ('Cloud Security Best Practices and Compliance', 'Cloud Computing (AWS/Google Cloud)', 'Intermediate', '18 hours',
             'Secure cloud environments against modern threats',
             'Study identity and access management, data encryption, network security, compliance frameworks (SOC 2, HIPAA, GDPR), and cloud-native security tools.',
             119.99),
            
            # Data Science
            ('Data Science Fundamentals with Python and Pandas', 'Data Science', 'Beginner', '22 hours',
             'Learn data manipulation, visualization, and exploratory analysis',
             'Master NumPy, Pandas, Matplotlib, and Seaborn. Clean, transform, and analyze real-world datasets. Learn statistical foundations for data science.',
             89.99),
            
            ('Statistical Modeling and Hypothesis Testing for Data Science', 'Data Science', 'Intermediate', '20 hours',
             'Apply statistical methods to draw meaningful conclusions from data',
             'Learn probability distributions, regression analysis, ANOVA, chi-square tests, and Bayesian statistics. Implement models in Python with SciPy and StatsModels.',
             94.99),
            
            ('Big Data Processing with Apache Spark', 'Data Science', 'Intermediate', '24 hours',
             'Process massive datasets efficiently with distributed computing',
             'Learn Spark RDDs, DataFrames, and SQL. Implement ETL pipelines, machine learning with MLlib, and graph processing with GraphX. Optimize Spark jobs for performance.',
             109.99),
            
            ('Data Visualization with Tableau and Power BI', 'Data Science', 'Beginner', '16 hours',
             'Create compelling visual stories from complex datasets',
             'Master dashboard creation, interactive visualizations, calculations, and storytelling techniques. Connect to various data sources and publish insights.',
             79.99),
            
            ('Experimental Design and A/B Testing for Data-Driven Decisions', 'Data Science', 'Advanced', '18 hours',
             'Design and analyze experiments to validate business hypotheses',
             'Learn randomization techniques, sample size calculation, statistical power, and multivariate testing. Apply to web analytics, product development, and marketing.',
             89.99),
            
            # DevOps
            ('DevOps Engineering: CI/CD Pipelines with Jenkins and GitLab', 'DevOps', 'Intermediate', '20 hours',
             'Automate software delivery from code commit to production',
             'Learn to build, test, and deploy applications using Jenkins and GitLab CI. Implement blue-green deployments, feature flags, and infrastructure as code.',
             99.99),
            
            ('Infrastructure as Code with Terraform and Ansible', 'DevOps', 'Intermediate', '18 hours',
             'Manage cloud infrastructure through declarative code',
             'Learn to provision AWS/Azure/GCP resources with Terraform. Configure servers and applications with Ansible. Implement drift detection and compliance checks.',
             109.99),
            
            ('Monitoring and Observability: Prometheus, Grafana, and ELK Stack', 'DevOps', 'Intermediate', '16 hours',
             'Gain deep insights into system performance and application behavior',
             'Learn to collect, store, and visualize metrics with Prometheus and Grafana. Implement centralized logging with ELK stack and distributed tracing with Jaeger.',
             89.99),
            
            ('Containerization with Docker and Kubernetes Administration', 'DevOps', 'Beginner', '22 hours',
             'Package applications and manage containerized workloads',
             'Master Docker images, containers, networking, and volumes. Learn Kubernetes pod management, services, ingress controllers, and Helm packaging.',
             119.99),
            
            ('Site Reliability Engineering (SRE): Building Reliable Systems', 'DevOps', 'Advanced', '20 hours',
             'Apply SRE principles to create highly available and scalable services',
             'Learn SLIs, SLAs, error budgets, incident management, chaos engineering, and capacity planning. Implement toil reduction and blameless postmortems.',
             129.99),
            
            # Additional courses to reach 50+
            ('Python for Everybody: Programming Fundamentals', 'Programming Fundamentals', 'Beginner', '30 hours',
             'Learn Python from basics to intermediate concepts',
             'Start with variables, data types, and control flow. Progress to functions, modules, file handling, and object-oriented programming. Build practical projects.',
             0),  # Free course
            
            ('JavaScript Deep Dive: ES6+ and Async Patterns', 'Programming Fundamentals', 'Intermediate', '25 hours',
             'Master modern JavaScript features and asynchronous programming',
             'Learn arrow functions, destructuring, spread/rest operators, modules, promises, async/await, and proxy objects. Build performant web applications.',
             69.99),
            
            ('TypeScript: Advanced Types and Project Setup', 'Programming Fundamentals', 'Intermediate', '18 hours',
             'Scale JavaScript applications with static typing',
             'Learn advanced type system features, decorators, namespaces, and project configuration. Migrate JavaScript projects to TypeScript with confidence.',
             59.99),
            
            ('Machine Learning for Finance: Predictive Modeling and Risk Analysis', 'Artificial Intelligence & Machine Learning', 'Advanced', '20 hours',
             'Apply ML techniques to financial data and risk management',
             'Learn time series forecasting, credit scoring, fraud detection, algorithmic trading, and portfolio optimization. Use Python with scikit-learn and TensorFlow.',
             139.99),
            
            ('Ethical AI: Bias Detection and Fairness in Machine Learning', 'Artificial Intelligence & Machine Learning', 'Intermediate', '16 hours',
             'Build responsible AI systems that treat all users fairly',
             'Learn to detect and mitigate bias in data and models. Study fairness metrics, interpretability techniques, and regulatory compliance for AI systems.',
             89.99),
            
            ('AWS Certified Developer Associate: Building Applications', 'Cloud Computing (AWS/Google Cloud)', 'Intermediate', '26 hours',
             'Prepare for AWS Developer certification with hands-on practice',
             'Learn to develop, deploy, and debug cloud-native applications using AWS services. Master SDKs, Lambda, API Gateway, DynamoDB, and CI/CD integration.',
             139.99),
            
            ('Google Cloud Data Engineering: Building Data Pipelines', 'Cloud Computing (AWS/Google Cloud)', 'Intermediate', '24 hours',
             'Learn to build and manage data processing systems on Google Cloud',
             'Master BigQuery, Dataflow, Pub/Sub, Dataproc, and Composer. Design ETL/ELT pipelines for batch and streaming data workloads.',
             129.99),
            
            ('Red Team Operations: Advanced Adversary Emulation', 'Cybersecurity & Ethical Hacking', 'Advanced', '30 hours',
             'Simulate real-world attacks to test organizational defenses',
             'Learn advanced persistence techniques, lateral movement, data exfiltration, and evasion tactics. Conduct full-scope penetration tests and red team operations.',
             159.99),
            
            ('Secure Software Development Lifecycle (SSDLC)', 'Cybersecurity & Ethical Hacking', 'Intermediate', '18 hours',
             'Integrate security practices throughout the development process',
             'Learn threat modeling, secure coding standards, security testing, and vulnerability management. Implement DevSecOps practices and security automation.',
             99.99),
            
            ('Natural Language Processing in Practice: SpaCy and NLTK', 'Artificial Intelligence & Machine Learning', 'Intermediate', '20 hours',
             'Process and analyze text data with popular Python libraries',
             'Learn tokenization, part-of-speech tagging, named entity recognition, sentiment analysis, and text classification. Build chatbots and information extraction systems.',
             79.99),
            
            ('Time Series Analysis and Forecasting', 'Data Science', 'Advanced', '22 hours',
             'Model and predict temporal data for business and scientific applications',
             'Learn ARIMA, exponential smoothing, state space models, and Prophet. Handle seasonality, trends, and external variables in forecasting models.',
             109.99),
            
            ('Data Engineering with Python: ETL Pipelines and Workflows', 'Data Science', 'Intermediate', '20 hours',
             'Build reliable data pipelines for analytics and machine learning',
             'Learn to extract data from various sources, transform it for analysis, and load it into data warehouses. Use Apache Airflow for workflow orchestration.',
             94.99),
            
            ('Linux System Administration: From Basics to Advanced', 'DevOps', 'Beginner', '28 hours',
             'Manage Linux systems in enterprise environments',
             'Learn user management, permissions, networking, security, shell scripting, and troubleshooting. Manage services, monitor performance, and automate tasks.',
             69.99),
            
            ('Database Administration: SQL and NoSQL Systems', 'DevOps', 'Intermediate', '24 hours',
             'Manage and optimize relational and non-relational databases',
             'Learn MySQL, PostgreSQL, MongoDB, and Redis administration. Cover backup/replication, performance tuning, security, and high availability configurations.',
             89.99),
            
            ('API Design and Development: REST, GraphQL, and gRPC', 'Full-Stack Web Development', 'Intermediate', '20 hours',
             'Design and build modern APIs for web and mobile applications',
             'Learn RESTful principles, GraphQL schema design, and gRPC implementation. Implement authentication, rate limiting, documentation, and versioning strategies.',
             89.99),
            
            ('Web Performance Optimization: Speed and User Experience', 'Full-Stack Web Development', 'Intermediate', '16 hours',
              'Make web applications fast and responsive across devices',
              'Learn critical rendering path optimization, lazy loading, image optimization, caching strategies, and core web vitals. Measure and improve performance metrics.',
              59.99),
            
            ('Introduction to Cybersecurity: Principles and Practices', 'Cybersecurity & Ethical Hacking', 'Beginner', '14 hours',
              'Learn the fundamentals of cybersecurity and information protection',
              'Explore key concepts including threat landscape, risk management, security policies, and basic cryptography. Hands-on labs with security tools and techniques.',
              0),  # Free course
            
            ('Advanced React Patterns: Performance and Scalability', 'Full-Stack Web Development', 'Advanced', '18 hours',
              'Master advanced React patterns for building scalable applications',
              'Learn render props, higher-order components, compound components, and advanced hooks. Performance optimization, code splitting, and server-side rendering with Next.js.',
              109.99),
            
            ('Data Science Leadership: Building and Managing Teams', 'Data Science', 'Advanced', '16 hours',
              'Learn to lead data science teams and drive data-driven decision making',
              'Cover team building, project management, communication of technical findings, and fostering a data-driven culture. Case studies from industry leaders.',
              89.99),
            
            ('Cloud Cost Optimization: Strategies for AWS and Azure', 'Cloud Computing (AWS/Google Cloud)', 'Intermediate', '12 hours',
              'Reduce cloud spending while maintaining performance and reliability',
              'Learn rightsizing, reserved instances, spot instances, cost monitoring, and optimization tools. Implement governance and tagging strategies for cost allocation.',
              79.99),
            
            ('Machine Learning Engineering: Production Systems', 'Artificial Intelligence & Machine Learning', 'Advanced', '22 hours',
              'Build and maintain machine learning systems in production environments',
              'Learn feature engineering, model validation, drift detection, and pipeline automation. Use MLflow, Kubeflow, and SageMaker for end-to-end ML workflows.',
              129.99),
        ]

        # Create courses
        created_count = 0
        for title, category, level, duration, summary, description, price in courses_data:
            # Generate slug from title
            slug = slugify(title)
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Course.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            # Assign random instructor
            instructor = random.choice(instructors) if instructors else None
            
            Course.objects.create(
                title=title,
                slug=slug,
                category=category,
                level=level,
                duration=duration,
                summary=summary,
                description=description,
                price=price,
                instructor=instructor,
                is_published=True
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} courses')
        )