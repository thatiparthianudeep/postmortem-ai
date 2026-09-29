"""
Mock Incidents Seed Dataset (Hindsight Memory Integration)
Contains historical production incidents used for pattern matching, 
Root Cause Analysis (RCA), and incident memory retrieval.
"""

from typing import List, Dict, Any

MOCK_INCIDENTS: List[Dict[Any, Any]] = [
    {
        "id": "INC-2025-0812",
        "title": "PostgreSQL Connection Pool Exhaustion during Flash Sale",
        "severity": "P0 - CRITICAL",
        "category": "Database & Infrastructure",
        "timestamp": "2025-08-12T00:02:00Z",
        "duration_minutes": 45,
        "impact_summary": "45 mins downtime on Checkout Service, 35% API request failures (500 & 504 Gateway Timeout). ~8,400 orders dropped.",
        "summary": "Surge in checkout microservices exhausted database connection pool without timeout limits, causing cascade failure across downstream services.",
        "root_cause": "Max DB connections set to 100 with default pool recycle time. High-concurrency checkout requests held open transactions waiting on external payment gateway response, depleting all connection slots.",
        "timeline": [
            {"time": "00:02 UTC", "event": "Datadog alert: Checkout API 500 error rate exceeded 15%"},
            {"time": "00:08 UTC", "event": "On-call engineer paged. PostgreSQL CPU reached 100%"},
            {"time": "00:15 UTC", "event": "PgBouncer logs revealed 100 active connections and 450 client connections waiting in queue"},
            {"time": "00:28 UTC", "event": "PgBouncer max_client_conn increased to 500 and connection checkout timeout set to 3000ms"},
            {"time": "00:47 UTC", "event": "Connection queue drained, API latency restored to normal (120ms baseline)"}
        ],
        "five_whys": [
            "Why did Checkout API fail? -> Database queries were timing out.",
            "Why were queries timing out? -> All PostgreSQL connections were exhausted.",
            "Why were connections exhausted? -> Requests were held open waiting for payment response without socket timeouts.",
            "Why were there no socket timeouts? -> Default connection pool settings were never updated during microservice split.",
            "Why were settings not updated? -> Lack of standardized DB pool configuration template across microservices."
        ],
        "action_items": [
            {"priority": "P0", "task": "Deploy PgBouncer sidecar with strict transaction-level pooling", "owner": "DevOps / Infra Team", "status": "COMPLETED"},
            {"priority": "P1", "task": "Implement circuit breaker and strict 3s HTTP timeout on Payment Gateway requests", "owner": "Payment Team", "status": "COMPLETED"},
            {"priority": "P2", "task": "Establish mandatory DB connection pool load testing in CI/CD pipeline", "owner": "QA / SRE", "status": "COMPLETED"}
        ],
        "tags": ["postgresql", "database", "connection-pool", "checkout", "p0", "timeout", "pgbouncer"]
    },
    {
        "id": "INC-2025-0904",
        "title": "Auth Microservice OOMKilled caused by JWT Memory Leak",
        "severity": "P1 - HIGH",
        "category": "Security & Memory Leak",
        "timestamp": "2025-09-04T14:10:00Z",
        "duration_minutes": 22,
        "impact_summary": "22 minutes of partial auth failures, ~15,000 user sessions forcibly logged out across web and mobile apps.",
        "summary": "Redis fallback in-memory LRU cache lacked max-element eviction policy. Revoked JWT token blacklist dictionary grew indefinitely until container RAM was exhausted.",
        "root_cause": "When Redis cluster underwent node failover, Auth service fallback to local Python memory cache. Python dict retained invalidated tokens without TTL expiration logic, triggering Kubernetes OOMKilled (Exit Code 137).",
        "timeline": [
            {"time": "14:10 UTC", "event": "Auth pod memory consumption spiked from 350MB to 1.9GB (Container limit 2.0GB)"},
            {"time": "14:15 UTC", "event": "Kubernetes master OOMKilled 4 out of 6 Auth service pods in crash loop"},
            {"time": "14:18 UTC", "event": "User login & token validation endpoints failing with 502 Bad Gateway"},
            {"time": "14:27 UTC", "event": "Hotfix deployed introducing TTLCache (maxsize=50000, ttl=3600s) for fallback cache"},
            {"time": "14:32 UTC", "event": "Pods stabilized, memory consumption locked at ~280MB"}
        ],
        "five_whys": [
            "Why did Auth pods crash loop? -> Containers exceeded memory limit and were terminated by Kubernetes OOMKilled.",
            "Why did memory spike? -> In-memory JWT revocation cache stored over 4,000,000 strings.",
            "Why did the cache store so many strings? -> Fallback cache used a plain unbounded Python dictionary.",
            "Why was a plain dictionary used? -> Redis fallback was designed as emergency backup and assumed brief failovers.",
            "Why did failover take so long? -> Redis sentinel failover config was misconfigured to wait 15 minutes before promoting replica."
        ],
        "action_items": [
            {"priority": "P0", "task": "Replace unbounded dict with bounded cache with strict TTL in auth engine", "owner": "Security Engineering", "status": "COMPLETED"},
            {"priority": "P1", "task": "Tune Redis Sentinel failover timeout from 900s down to 15s", "owner": "Infra Team", "status": "COMPLETED"},
            {"priority": "P2", "task": "Add Prometheus alert for pod memory utilization > 80%", "owner": "Observability Team", "status": "COMPLETED"}
        ],
        "tags": ["redis", "auth", "memory-leak", "cache", "oom", "kubernetes", "jwt", "p1"]
    },
    {
        "id": "INC-2025-1019",
        "title": "DNS Resolution Timeout during Cloud Provider Migration",
        "severity": "P1 - HIGH",
        "category": "Networking & DNS",
        "timestamp": "2025-10-19T03:00:00Z",
        "duration_minutes": 12,
        "impact_summary": "Global API unreachable for mobile applications for 12 minutes. 100% request failure on api.company.com domain.",
        "summary": "CoreDNS pods cached stale IP address records following AWS Route53 record update. High DNS TTL settings prevented fast failover propagation.",
        "root_cause": "The DNS TTL for api.company.com was set to 86400s (24 hours). When traffic was switched to new NLB target group IPs, internal CoreDNS and external resolvers routed traffic to decommissioned load balancers.",
        "timeline": [
            {"time": "03:00 UTC", "event": "Cutover initiated: Route53 A-record changed to point to New AWS NLB IP"},
            {"time": "03:02 UTC", "event": "Synthetics monitor alerted DNS lookup failure and connection timeout"},
            {"time": "03:07 UTC", "event": "Incident commander realized TTL was 86400s instead of pre-agreed 60s"},
            {"time": "03:10 UTC", "event": "Executed DNS flush on CoreDNS deployment and updated upstream resolver cache"},
            {"time": "03:12 UTC", "event": "Traffic routed successfully to new NLB, error rates dropped to 0%"}
        ],
        "five_whys": [
            "Why was api.company.com unreachable? -> Requests resolved to legacy non-existent load balancer IP.",
            "Why did resolvers return legacy IP? -> DNS TTL had not expired.",
            "Why was DNS TTL set to 24 hours? -> Pre-migration playbook step to reduce TTL to 60s 48 hours prior was missed.",
            "Why was that step missed? -> Change management checklist was manual and executed without peer verification.",
            "Why was it manual? -> Infrastructure DNS changes were not fully automated via Terraform."
        ],
        "action_items": [
            {"priority": "P0", "task": "Import all Route53 DNS records into Terraform with automated TTL validation", "owner": "Cloud Infra Team", "status": "COMPLETED"},
            {"priority": "P1", "task": "Automate migration cutover pre-checks script to block deployment if TTL > 300s", "owner": "Release Ops", "status": "COMPLETED"}
        ],
        "tags": ["dns", "coredns", "route53", "migration", "network", "aws", "p1", "ttl"]
    },
    {
        "id": "INC-2025-1102",
        "title": "Payment Gateway Webhook Race Condition causing Double Billing",
        "severity": "P0 - CRITICAL",
        "category": "Financial & Race Condition",
        "timestamp": "2025-11-02T11:20:00Z",
        "duration_minutes": 40,
        "impact_summary": "140 duplicate charges executed on customer credit cards, total value $38,500. Support queue surge of 400+ tickets.",
        "summary": "Stripe webhook retry mechanisms delivered identical webhook events simultaneously across 2 API worker instances, creating duplicate order rows due to missing database row lock.",
        "root_cause": "The webhook handler lacked distributed idempotency locking (e.g. Redis Redlock). Simultaneous HTTP POST requests entered order processing logic in parallel, checking `SELECT * FROM orders WHERE payment_id = ?` before either committed a transaction.",
        "timeline": [
            {"time": "11:20 UTC", "event": "Customer support reported multiple complaints of double billing for single checkout"},
            {"time": "11:25 UTC", "event": "Engineers discovered duplicate `payment_intent.succeeded` events processed 12ms apart"},
            {"time": "11:35 UTC", "event": "Hotfix deployed injecting Redis distributed lock keyed by `webhook_event_id`"},
            {"time": "11:50 UTC", "event": "Audited database: identified 140 impacted accounts and initiated automatic refunds"},
            {"time": "12:00 UTC", "event": "Incident closed, notification sent to affected users"}
        ],
        "five_whys": [
            "Why were customers double billed? -> Two order confirmation workflows ran concurrently for one payment.",
            "Why did two workflows run concurrently? -> Stripe sent duplicate webhooks in quick succession during network glitch.",
            "Why did our backend process both webhooks? -> The idempotency check was a non-atomic read-then-write operation.",
            "Why was it non-atomic? -> No Redis lock or unique constraint on `payment_id` column existed in DB schema.",
            "Why was unique constraint missing? -> Database schema migration omitted standard unique constraint during initial MVP phase."
        ],
        "action_items": [
            {"priority": "P0", "task": "Add UNIQUE INDEX on `orders.payment_intent_id` in Postgres schema", "owner": "Core Backend Team", "status": "COMPLETED"},
            {"priority": "P0", "task": "Enforce Redis distributed lock middleware on all webhook ingestion endpoints", "owner": "Payment Engineering", "status": "COMPLETED"},
            {"priority": "P1", "task": "Build automated double-billing detection background worker alerting within 60s", "owner": "Finance Tech", "status": "COMPLETED"}
        ],
        "tags": ["payment", "webhook", "race-condition", "idempotency", "redis-lock", "stripe", "p0", "financial"]
    },
    {
        "id": "INC-2025-1128",
        "title": "AWS S3 Storage Rate-Limit Bottleneck on Log Ingestion Pipeline",
        "severity": "P2 - MEDIUM",
        "category": "Storage & Data Pipeline",
        "timestamp": "2025-11-28T18:00:00Z",
        "duration_minutes": 180,
        "impact_summary": "Log ingestion pipeline lagged by 3.5 hours. Real-time audit dashboards delayed, but no end-user outage.",
        "summary": "Log shipping Fluentd agents attempted to write >4,000 PUT requests/sec to a single S3 bucket folder prefix `logs/2025/11/28/`, exceeding AWS S3 request rate limits.",
        "root_cause": "AWS S3 supports 3,500 PUT requests per second per partition prefix. By putting all raw log files in a flat timestamp path without prefix randomization, Fluentd encountered HTTP 503 Slow Down rate limiting.",
        "timeline": [
            {"time": "18:00 UTC", "event": "Datadog alert: Fluentd buffer queue length > 10,000 files"},
            {"time": "18:30 UTC", "event": "AWS CloudWatch showed S3 503 SlowDown errors spiking on log-vault bucket"},
            {"time": "19:15 UTC", "event": "Deployed updated Fluentd configuration adding high-entropy hash prefixes (`logs/{hash}/2025/11/28/`)"},
            {"time": "21:00 UTC", "event": "Log backlog completely processed, buffer queues cleared"}
        ],
        "five_whys": [
            "Why was log ingestion lagging? -> Fluentd workers received 503 SlowDown responses from AWS S3.",
            "Why was S3 throttling requests? -> Bucket prefix exceeded 3,500 PUTs/sec AWS throughput threshold.",
            "Why were all PUTs directed to one prefix? -> S3 object key format was `logs/YYYY/MM/DD/file.log`.",
            "Why was this key format chosen? -> Simple partition key chosen during initial log pipeline setup without anticipating scale growth.",
            "Why was scale threshold not caught earlier? -> Cyber Monday traffic surge increased log volume by 400%."
        ],
        "action_items": [
            {"priority": "P1", "task": "Update S3 bucket key schema to include MD5 hash prefix for partition splitting", "owner": "Data Platform Team", "status": "COMPLETED"},
            {"priority": "P2", "task": "Configure S3 auto-scaling partition guidelines in architectural docs", "owner": "Data Platform Team", "status": "COMPLETED"}
        ],
        "tags": ["aws-s3", "rate-limit", "logging", "pipeline", "storage", "fluentd", "p2", "503-slowdown"]
    },
    {
        "id": "INC-2025-1215",
        "title": "Kafka Consumer Group Lag Surge following Schema Registry Update",
        "severity": "P2 - MEDIUM",
        "category": "Streaming & Event Bus",
        "timestamp": "2025-12-15T16:30:00Z",
        "duration_minutes": 45,
        "impact_summary": "Recommendation engine updates delayed by 45 minutes for 1.2M online users.",
        "summary": "Incompatible Avro schema change committed to Kafka Schema Registry caused downstream consumers to throw DeserializationException in an infinite retry loop without Dead Letter Queue (DLQ).",
        "root_cause": "A non-optional field `user_tier_v2` was added to `OrderPlacedEvent` schema without default value. Consumers running v1 code failed to parse incoming v2 messages and blocked partition offsets.",
        "timeline": [
            {"time": "16:30 UTC", "event": "Deployment of order-service v2.4 introducing new event schema"},
            {"time": "16:35 UTC", "event": "Recommendation Service consumer group lag jumped from 10 msgs to 450,000 msgs"},
            {"time": "16:45 UTC", "event": "Logs showed thousands of `SerializationException: Error deserializing Avro message`"},
            {"time": "17:05 UTC", "event": "Hotfix deployed adding backward-compatible default value (`null`) in Schema Registry and DLQ routing"},
            {"time": "17:15 UTC", "event": "Poison pill messages routed to DLQ, consumer lag returned to zero"}
        ],
        "five_whys": [
            "Why did consumer lag spike? -> Recommendation workers were crashing continuously when consuming messages.",
            "Why were workers crashing? -> Failed to deserialize Avro payload due to schema field mismatch.",
            "Why was schema incompatible? -> Field `user_tier_v2` was declared required instead of optional.",
            "Why did Schema Registry allow breaking schema? -> Schema compatibility mode was accidentally set to `NONE` instead of `BACKWARD`.",
            "Why was compatibility mode set to NONE? -> Schema Registry settings were modified during emergency fix last month and not reverted."
        ],
        "action_items": [
            {"priority": "P0", "task": "Lock Schema Registry compatibility mode to `BACKWARD_TRANSITIVE` via CI check", "owner": "Data Engineering", "status": "COMPLETED"},
            {"priority": "P1", "task": "Enforce mandatory Dead Letter Queue (DLQ) pattern on all Kafka consumer microservices", "owner": "Architecture Guild", "status": "COMPLETED"}
        ],
        "tags": ["kafka", "schema-registry", "dlq", "consumer-lag", "events", "avro", "p2"]
    }
]

def get_all_incidents() -> List[Dict[Any, Any]]:
    """Returns the seed list of historical incidents."""
    return MOCK_INCIDENTS
