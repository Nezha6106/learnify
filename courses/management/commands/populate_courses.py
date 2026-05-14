from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import Course
import random

MAX_STR_LEN = 44  # Strictly under 45 characters


def truncate(text, max_len=MAX_STR_LEN):
    """Truncate string to max_len characters at a word boundary."""
    if len(text) <= max_len:
        return text
    cut = text[:max_len].rfind(' ')
    if cut == -1:
        cut = max_len
    return text[:cut].rstrip()


class Command(BaseCommand):
    help = 'Populate the database with realistic tech courses'

    def handle(self, *args, **options):
        if Course.objects.exists():
            self.stdout.write(
                self.style.WARNING('Courses already exist in database. Skipping population.')
            )
            return

        instructor_names = [
            'Alex Johnson', 'Maria Garcia', 'David Chen', 'Sarah Williams',
            'Robert Kim', 'Jennifer Davis', 'Michael Brown', 'Laura Miller',
            'James Wilson', 'Emily Taylor', 'Daniel Anderson', 'Olivia Thomas'
        ]

        instructors = []
        for name in instructor_names:
            first_name, last_name = name.split(' ', 1)
            username = f"{first_name.lower()}_{last_name.lower()}"
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

            email = f"{username}@learnify.com"
            if len(email) > MAX_STR_LEN:
                email = email[:MAX_STR_LEN]

            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': truncate(first_name),
                    'last_name': truncate(last_name),
                    'email': email,
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            if created:
                user.set_password('instructor123')
                user.save()
            instructors.append(user)

        courses_data = [
            (truncate('React.js Complete Guide: Build Modern Web Apps'),
             truncate('Full-Stack Web Development'), 'Beginner', '12 hours',
             truncate('Learn React from scratch to building production-ready applications'),
             truncate('Master React.js with hooks, context API, routing, and state management. Build 3 real-world projects.'),
             89.99),

            (truncate('Full-Stack Development with Node.js and MongoDB'),
             truncate('Full-Stack Web Development'), 'Intermediate', '18 hours',
             truncate('Build scalable REST APIs and connect them with modern frontend frameworks'),
             truncate('Learn to build robust backends with Node.js, Express, and MongoDB. Implement auth, file uploads, and CI/CD.'),
             99.99),

            (truncate('Vue 3 Masterclass: Composition API and Vuex'),
             truncate('Full-Stack Web Development'), 'Intermediate', '15 hours',
             truncate('Deep dive into Vue 3s reactivity system and state management'),
             truncate('Explore the Composition API, Vuex 4, and Vue Router 4. Build enterprise apps with TypeScript.'),
             79.99),

            (truncate('Angular Enterprise Application Development'),
             truncate('Full-Stack Web Development'), 'Advanced', '22 hours',
             truncate('Architect and build large-scale Angular applications'),
             truncate('Learn Angular CLI, RxJS, NgRx state management, and advanced component patterns with auth.'),
             119.99),

            (truncate('Progressive Web Apps with Service Workers'),
             truncate('Full-Stack Web Development'), 'Intermediate', '8 hours',
             truncate('Create offline-capable web apps that feel native'),
             truncate('Implement service workers, caching strategies, push notifications, and app manifest files.'),
             69.99),

            (truncate('Machine Learning Foundations: Linear Regression to Neural Nets'),
             truncate('Artificial Intelligence & Machine Learning'), 'Beginner', '20 hours',
             truncate('Understand core ML algorithms and implement them from scratch'),
             truncate('Start with linear regression and progress through decision trees, SVM, k-means, and neural networks.'),
             89.99),

            (truncate('Deep Learning with TensorFlow 2 and Keras'),
             truncate('Artificial Intelligence & Machine Learning'), 'Intermediate', '25 hours',
             truncate('Build and deploy neural networks for vision and NLP'),
             truncate('Master convolutional networks, recurrent networks, and transformer architectures. Deploy with TF Serving.'),
             109.99),

            (truncate('Natural Language Processing with Transformers'),
             truncate('Artificial Intelligence & Machine Learning'), 'Advanced', '18 hours',
             truncate('Work with state-of-the-art language models like BERT and GPT'),
             truncate('Learn tokenization, embeddings, fine-tuning pre-trained models, and building sentiment analysis and chatbots.'),
             129.99),

            (truncate('Computer Vision with OpenCV and Deep Learning'),
             truncate('Artificial Intelligence & Machine Learning'), 'Intermediate', '16 hours',
             truncate('Process and analyze visual data using traditional and deep learning'),
             truncate('Build face detection, object tracking, image segmentation, and OCR applications. Combine OpenCV with DL.'),
             94.99),

            (truncate('MLOps: Deploying ML Models at Scale'),
             truncate('Artificial Intelligence & Machine Learning'), 'Advanced', '14 hours',
             truncate('Learn to productionize ML models with monitoring and scaling'),
             truncate('Cover model versioning, A/B testing, Docker, Kubernetes orchestration, and CI/CD pipelines for ML.'),
             139.99),

            (truncate('Ethical Hacking: Penetration Testing and Vuln Assessment'),
             truncate('Cybersecurity & Ethical Hacking'), 'Beginner', '24 hours',
             truncate('Learn to think like a hacker to defend systems effectively'),
             truncate('Master reconnaissance, scanning, exploitation, and post-exploitation. Use Kali, Metasploit, Burp Suite.'),
             119.99),

            (truncate('Network Security Fundamentals and Firewall Config'),
             truncate('Cybersecurity & Ethical Hacking'), 'Beginner', '15 hours',
             truncate('Protect network infrastructure from common threats'),
             truncate('Study TCP/IP, firewall rules, IDS/IPS, VPN technologies, and wireless security. Implement defense-in-depth.'),
             89.99),

            (truncate('Web Application Security: OWASP Top 10 and Secure Coding'),
             truncate('Cybersecurity & Ethical Hacking'), 'Intermediate', '20 hours',
             truncate('Identify and fix security vulnerabilities in web apps'),
             truncate('Learn about injection attacks, broken auth, sensitive data exposure, and XXE. Implement secure coding.'),
             99.99),

            (truncate('Cryptography and Blockchain Security Fundamentals'),
             truncate('Cybersecurity & Ethical Hacking'), 'Advanced', '18 hours',
             truncate('Understand modern cryptographic techniques and applications'),
             truncate('Study symmetric/asymmetric encryption, hashing, digital signatures, zero-knowledge proofs, and blockchain.'),
             129.99),

            (truncate('Incident Response and Digital Forensics'),
             truncate('Cybersecurity & Ethical Hacking'), 'Intermediate', '22 hours',
             truncate('Detect, respond to, and investigate security breaches'),
             truncate('Learn evidence collection, malware analysis, memory forensics, network forensics, and legal aspects.'),
             109.99),

            (truncate('AWS Solutions Architect Associate Complete Course'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Beginner', '30 hours',
             truncate('Prepare for AWS SAA-C03 certification with hands-on labs'),
             truncate('Master EC2, S3, VPC, RDS, Lambda, and CloudFormation. Design highly available and cost-effective systems.'),
             149.99),

            (truncate('Google Cloud Professional Cloud Architect Certification'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Beginner', '28 hours',
             truncate('Prepare for Google Cloud PCA certification with exercises'),
             truncate('Learn Compute Engine, Cloud Storage, VPC, BigQuery, Kubernetes Engine, and Deployment Manager.'),
             149.99),

            (truncate('Serverless Architecture with AWS Lambda and API Gateway'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Intermediate', '16 hours',
             truncate('Build event-driven apps without managing servers'),
             truncate('Create REST APIs with Lambda and API Gateway, implement event-driven architectures, monitor with CloudWatch.'),
             119.99),

            (truncate('Kubernetes Deep Dive: Orchestration at Scale'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Advanced', '24 hours',
             truncate('Master container orchestration with Kubernetes'),
             truncate('Learn pod networking, storage, security, Helm charts, operators, and GitOps. Troubleshoot with Prometheus.'),
             139.99),

            (truncate('Cloud Security Best Practices and Compliance'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Intermediate', '18 hours',
             truncate('Secure cloud environments against modern threats'),
             truncate('Study IAM, data encryption, network security, compliance frameworks, and cloud-native security tools.'),
             119.99),

            (truncate('Data Science Fundamentals with Python and Pandas'),
             truncate('Data Science'), 'Beginner', '22 hours',
             truncate('Learn data manipulation, visualization, and exploratory analysis'),
             truncate('Master NumPy, Pandas, Matplotlib, and Seaborn. Clean, transform, and analyze real-world datasets.'),
             89.99),

            (truncate('Statistical Modeling and Hypothesis Testing for Data Science'),
             truncate('Data Science'), 'Intermediate', '20 hours',
             truncate('Apply statistical methods to draw meaningful conclusions'),
             truncate('Learn probability distributions, regression, ANOVA, chi-square tests, and Bayesian statistics with SciPy.'),
             94.99),

            (truncate('Big Data Processing with Apache Spark'),
             truncate('Data Science'), 'Intermediate', '24 hours',
             truncate('Process massive datasets efficiently with distributed computing'),
             truncate('Learn Spark RDDs, DataFrames, and SQL. Implement ETL, MLlib, and GraphX. Optimize Spark jobs.'),
             109.99),

            (truncate('Data Visualization with Tableau and Power BI'),
             truncate('Data Science'), 'Beginner', '16 hours',
             truncate('Create compelling visual stories from complex datasets'),
             truncate('Master dashboard creation, interactive visualizations, calculations, and storytelling. Publish insights.'),
             79.99),

            (truncate('Experimental Design and A/B Testing for Data Decisions'),
             truncate('Data Science'), 'Advanced', '18 hours',
             truncate('Design and analyze experiments to validate business hypotheses'),
             truncate('Learn randomization, sample size calculation, statistical power, and multivariate testing for analytics.'),
             89.99),

            (truncate('DevOps Engineering: CI/CD Pipelines with Jenkins and GitLab'),
             truncate('DevOps'), 'Intermediate', '20 hours',
             truncate('Automate software delivery from code commit to production'),
             truncate('Build, test, and deploy apps using Jenkins and GitLab CI. Implement blue-green deployments and IaC.'),
             99.99),

            (truncate('Infrastructure as Code with Terraform and Ansible'),
             truncate('DevOps'), 'Intermediate', '18 hours',
             truncate('Manage cloud infrastructure through declarative code'),
             truncate('Provision AWS/Azure/GCP with Terraform. Configure servers with Ansible. Implement drift detection.'),
             109.99),

            (truncate('Monitoring and Observability: Prometheus, Grafana, ELK'),
             truncate('DevOps'), 'Intermediate', '16 hours',
             truncate('Gain deep insights into system performance and behavior'),
             truncate('Collect, store, and visualize metrics with Prometheus and Grafana. Centralized logging with ELK and Jaeger.'),
             89.99),

            (truncate('Containerization with Docker and Kubernetes Admin'),
             truncate('DevOps'), 'Beginner', '22 hours',
             truncate('Package applications and manage containerized workloads'),
             truncate('Master Docker images, containers, networking, and volumes. Learn Kubernetes pod management and Helm.'),
             119.99),

            (truncate('Site Reliability Engineering: Building Reliable Systems'),
             truncate('DevOps'), 'Advanced', '20 hours',
             truncate('Apply SRE principles to create highly available and scalable services'),
             truncate('Learn SLIs, SLAs, error budgets, incident management, chaos engineering, and toil reduction.'),
             129.99),

            (truncate('Python for Everybody: Programming Fundamentals'),
             truncate('Programming Fundamentals'), 'Beginner', '30 hours',
             truncate('Learn Python from basics to intermediate concepts'),
             truncate('Start with variables, data types, control flow. Progress to functions, modules, file handling, and OOP.'),
             0),

            (truncate('JavaScript Deep Dive: ES6+ and Async Patterns'),
             truncate('Programming Fundamentals'), 'Intermediate', '25 hours',
             truncate('Master modern JavaScript features and async programming'),
             truncate('Learn arrow functions, destructuring, spread/rest, modules, promises, async/await, and proxy objects.'),
             69.99),

            (truncate('TypeScript: Advanced Types and Project Setup'),
             truncate('Programming Fundamentals'), 'Intermediate', '18 hours',
             truncate('Scale JavaScript applications with static typing'),
             truncate('Learn advanced type system features, decorators, namespaces, and config. Migrate JS to TypeScript.'),
             59.99),

            (truncate('Machine Learning for Finance: Predictive Modeling'),
             truncate('Artificial Intelligence & Machine Learning'), 'Advanced', '20 hours',
             truncate('Apply ML techniques to financial data and risk management'),
             truncate('Learn time series forecasting, credit scoring, fraud detection, trading, and portfolio optimization.'),
             139.99),

            (truncate('Ethical AI: Bias Detection and Fairness in ML'),
             truncate('Artificial Intelligence & Machine Learning'), 'Intermediate', '16 hours',
             truncate('Build responsible AI systems that treat users fairly'),
             truncate('Detect and mitigate bias in data and models. Study fairness metrics, interpretability, and compliance.'),
             89.99),

            (truncate('AWS Certified Developer Associate: Building Apps'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Intermediate', '26 hours',
             truncate('Prepare for AWS Developer certification with practice'),
             truncate('Develop, deploy, and debug cloud-native apps using AWS. Master SDKs, Lambda, API Gateway, DynamoDB.'),
             139.99),

            (truncate('Google Cloud Data Engineering: Building Pipelines'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Intermediate', '24 hours',
             truncate('Build and manage data processing systems on Google Cloud'),
             truncate('Master BigQuery, Dataflow, Pub/Sub, Dataproc, and Composer. Design ETL/ELT pipelines.'),
             129.99),

            (truncate('Red Team Operations: Advanced Adversary Emulation'),
             truncate('Cybersecurity & Ethical Hacking'), 'Advanced', '30 hours',
             truncate('Simulate real-world attacks to test organizational defenses'),
             truncate('Learn advanced persistence, lateral movement, data exfiltration, and evasion. Conduct full-scope pentests.'),
             159.99),

            (truncate('Secure Software Development Lifecycle (SSDLC)'),
             truncate('Cybersecurity & Ethical Hacking'), 'Intermediate', '18 hours',
             truncate('Integrate security practices throughout the development process'),
             truncate('Learn threat modeling, secure coding, security testing, and vuln management. Implement DevSecOps.'),
             99.99),

            (truncate('Natural Language Processing in Practice: SpaCy, NLTK'),
             truncate('Artificial Intelligence & Machine Learning'), 'Intermediate', '20 hours',
             truncate('Process and analyze text data with popular Python libraries'),
             truncate('Learn tokenization, POS tagging, named entity recognition, sentiment analysis, and text classification.'),
             79.99),

            (truncate('Time Series Analysis and Forecasting'),
             truncate('Data Science'), 'Advanced', '22 hours',
             truncate('Model and predict temporal data for business applications'),
             truncate('Learn ARIMA, exponential smoothing, state space models, and Prophet. Handle seasonality and trends.'),
             109.99),

            (truncate('Data Engineering with Python: ETL Pipelines'),
             truncate('Data Science'), 'Intermediate', '20 hours',
             truncate('Build reliable data pipelines for analytics and ML'),
             truncate('Extract, transform, and load data into warehouses. Use Apache Airflow for workflow orchestration.'),
             94.99),

            (truncate('Linux System Administration: Basics to Advanced'),
             truncate('DevOps'), 'Beginner', '28 hours',
             truncate('Manage Linux systems in enterprise environments'),
             truncate('Learn user management, permissions, networking, security, shell scripting, and troubleshooting.'),
             69.99),

            (truncate('Database Administration: SQL and NoSQL Systems'),
             truncate('DevOps'), 'Intermediate', '24 hours',
             truncate('Manage and optimize relational and non-relational databases'),
             truncate('Learn MySQL, PostgreSQL, MongoDB, and Redis admin. Cover backup, tuning, security, and high availability.'),
             89.99),

            (truncate('API Design: REST, GraphQL, and gRPC'),
             truncate('Full-Stack Web Development'), 'Intermediate', '20 hours',
             truncate('Design and build modern APIs for web and mobile apps'),
             truncate('Learn RESTful principles, GraphQL schema design, and gRPC. Implement auth, rate limiting, and versioning.'),
             89.99),

            (truncate('Web Performance Optimization: Speed and UX'),
             truncate('Full-Stack Web Development'), 'Intermediate', '16 hours',
             truncate('Make web apps fast and responsive across devices'),
             truncate('Learn critical rendering path, lazy loading, image optimization, caching, and core web vitals.'),
             59.99),

            (truncate('Introduction to Cybersecurity: Principles and Practices'),
             truncate('Cybersecurity & Ethical Hacking'), 'Beginner', '14 hours',
             truncate('Learn cybersecurity fundamentals and information protection'),
             truncate('Explore threat landscape, risk management, security policies, and basic cryptography. Hands-on labs.'),
             0),

            (truncate('Advanced React Patterns: Performance and Scalability'),
             truncate('Full-Stack Web Development'), 'Advanced', '18 hours',
             truncate('Master advanced React patterns for scalable applications'),
             truncate('Learn render props, higher-order components, compound components, advanced hooks, and Next.js SSR.'),
             109.99),

            (truncate('Data Science Leadership: Building and Managing Teams'),
             truncate('Data Science'), 'Advanced', '16 hours',
             truncate('Lead data science teams and drive data-driven decisions'),
             truncate('Cover team building, project management, communication of findings, and data-driven culture.'),
             89.99),

            (truncate('Cloud Cost Optimization: Strategies for AWS and Azure'),
             truncate('Cloud Computing (AWS/Google Cloud)'), 'Intermediate', '12 hours',
             truncate('Reduce cloud spending while maintaining performance'),
             truncate('Learn rightsizing, reserved instances, spot instances, cost monitoring, and optimization tools.'),
             79.99),

            (truncate('Machine Learning Engineering: Production Systems'),
             truncate('Artificial Intelligence & Machine Learning'), 'Advanced', '22 hours',
             truncate('Build and maintain ML systems in production environments'),
             truncate('Learn feature engineering, model validation, drift detection, and pipeline automation. Use MLflow.'),
             129.99),
        ]

        created_count = 0
        for title, category, level, duration, summary, description, price in courses_data:
            slug = slugify(title)
            counter = 1
            original_slug = slug
            while Course.objects.filter(slug=slug).exists():
                suffix = f"-{counter}"
                slug = original_slug[:44 - len(suffix)] + suffix
                counter += 1

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