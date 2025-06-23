from typing import Dict, Any, List
import json
import asyncio
# Mock ADK Classes
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import json

class Message:
    def __init__(self, content: str, sender: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.sender = sender
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"msg_{hash(content + sender + str(datetime.now()))}"

class LlmAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.description = ""
        self.created_at = datetime.now().isoformat()
        self.message_history: List[Message] = []
    
    @abstractmethod
    async def run(self, message: Message) -> Message:
        pass
import openai
import anthropic
import os

class PlannerAgent(LlmAgent):
    def __init__(self, name: str = "planner_agent", llm_provider: str = "openrouter"):
        super().__init__(name=name)
        self.description = "Plans n8n workflow structure based on user requirements"
        self.llm_provider = llm_provider
        self._setup_llm()
    
    def _setup_llm(self):
        """Setup LLM client based on provider"""
        try:
            if self.llm_provider == "openrouter":
                api_key = os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    print("Warning: OPENROUTER_API_KEY not set, using fallback mode")
                    self.client = None
                    return
                    
                self.client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key
                )
                self.model = "anthropic/claude-3.5-sonnet"
            elif self.llm_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    print("Warning: ANTHROPIC_API_KEY not set, using fallback mode")
                    self.client = None
                    return
                    
                self.client = anthropic.Anthropic(
                    api_key=api_key
                )
                self.model = "claude-3-sonnet-20240229"
        except Exception as e:
            print(f"LLM setup failed: {e}")
            self.client = None
    
    async def plan_workflow(self, user_input: str) -> Dict[str, Any]:
        """Create a detailed plan for the n8n workflow"""
        try:
            # If no LLM client available, use fallback immediately
            if not self.client:
                print("No LLM client available, using fallback plan")
                plan = self._create_fallback_plan(user_input)
                plan["status"] = "success"
                plan["timestamp"] = self._get_timestamp()
                plan["note"] = "Generated using fallback mode (no API key)"
                return plan
            
            planning_prompt = f"""
            You are an expert n8n workflow architect. Given the user requirement below, create a detailed plan for an n8n workflow.

            User Requirement: {user_input}

            Please provide a structured plan that includes:
            1. Workflow overview and purpose
            2. Required nodes and their types
            3. Node connections and flow
            4. Data transformations needed
            5. Error handling considerations
            6. Expected outputs

            Format your response as a JSON object with the following structure:
            {{
                "workflow_name": "descriptive name",
                "description": "workflow purpose",
                "nodes": [
                    {{
                        "id": "node_id",
                        "type": "n8n-node-type",
                        "name": "Node Name",
                        "description": "what this node does",
                        "parameters": {{}},
                        "position": [x, y]
                    }}
                ],
                "connections": [
                    {{
                        "from": "source_node_id",
                        "to": "target_node_id",
                        "output_index": 0,
                        "input_index": 0
                    }}
                ],
                "estimated_complexity": "low|medium|high",
                "required_credentials": []
            }}
            """
            
            try:
                if self.llm_provider == "openrouter":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": planning_prompt}],
                        temperature=0.3,
                        max_tokens=2000
                    )
                    plan_text = response.choices[0].message.content
                else:
                    response = self.client.messages.create(
                        model=self.model,
                        max_tokens=2000,
                        temperature=0.3,
                        messages=[{"role": "user", "content": planning_prompt}]
                    )
                    plan_text = response.content[0].text
                
                # Parse JSON response
                try:
                    plan = json.loads(plan_text)
                except json.JSONDecodeError:
                    print("Failed to parse LLM response as JSON, using fallback")
                    plan = self._create_fallback_plan(user_input)
                
            except Exception as api_error:
                print(f"LLM API call failed: {api_error}")
                plan = self._create_fallback_plan(user_input)
                plan["note"] = f"LLM API failed: {str(api_error)}"
            
            plan["status"] = "success"
            plan["timestamp"] = self._get_timestamp()
            
            return plan
            
        except Exception as e:
            print(f"Planning failed with error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": self._get_timestamp(),
                "fallback_plan": self._create_fallback_plan(user_input)
            }
    
    def _create_fallback_plan(self, user_input: str) -> Dict[str, Any]:
        """Create intelligent fallback plan based on input keywords"""
        input_lower = user_input.lower()
        
        # More sophisticated keyword detection
        if any(word in input_lower for word in ["webhook", "api", "receive", "endpoint"]):
            return self._create_webhook_plan(user_input)
        elif any(word in input_lower for word in ["rss", "feed", "monitor", "check"]):
            return self._create_rss_plan(user_input)
        elif any(word in input_lower for word in ["csv", "file", "upload", "process", "data"]):
            return self._create_file_plan(user_input)
        elif any(word in input_lower for word in ["email", "mail", "notification", "alert"]):
            return self._create_email_plan(user_input)
        elif any(word in input_lower for word in ["youtube", "video", "channel", "social media", "posts", "schedule"]):
            return self._create_social_media_plan(user_input)
        elif any(word in input_lower for word in ["github", "jira", "slack", "integration", "api"]):
            return self._create_api_integration_plan(user_input)
        elif any(word in input_lower for word in ["order", "ecommerce", "e-commerce", "payment", "inventory"]):
            return self._create_ecommerce_plan(user_input)
        elif any(word in input_lower for word in ["test", "testing", "qa", "quality", "automation"]):
            return self._create_testing_plan(user_input)
        elif any(word in input_lower for word in ["developer", "development", "code", "deploy", "build"]):
            return self._create_developer_plan(user_input)
        else:
            return self._create_intelligent_generic_plan(user_input)
    
    def _create_webhook_plan(self, user_input: str) -> Dict[str, Any]:
        """Create webhook-specific plan"""
        return {
            "workflow_name": f"Webhook Workflow: {user_input[:30]}...",
            "description": f"Webhook-based workflow for: {user_input}",
            "nodes": [
                {
                    "id": "webhook_trigger",
                    "type": "n8n-nodes-base.webhook",
                    "name": "Webhook Trigger",
                    "description": "Receives webhook data",
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "webhook-data",
                        "responseMode": "onReceived"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "process_data",
                    "type": "n8n-nodes-base.code",
                    "name": "Process Data",
                    "description": "Processes incoming webhook data",
                    "parameters": {
                        "jsCode": "// Process webhook data\nconst data = items[0].json;\nreturn [{json: {processed: true, data: data}}];"
                    },
                    "position": [450, 300]
                },
                {
                    "id": "response",
                    "type": "n8n-nodes-base.respondToWebhook",
                    "name": "Respond",
                    "description": "Send response back",
                    "parameters": {
                        "respondWith": "json",
                        "responseBody": '{"status": "success"}'
                    },
                    "position": [650, 300]
                }
            ],
            "connections": [
                {"from": "webhook_trigger", "to": "process_data", "output_index": 0, "input_index": 0},
                {"from": "process_data", "to": "response", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "medium",
            "required_credentials": []
        }
    
    def _create_rss_plan(self, user_input: str) -> Dict[str, Any]:
        """Create RSS monitoring plan"""
        return {
            "workflow_name": f"RSS Monitor: {user_input[:30]}...",
            "description": f"RSS monitoring workflow for: {user_input}",
            "nodes": [
                {
                    "id": "rss_trigger",
                    "type": "n8n-nodes-base.rssFeedRead",
                    "name": "RSS Feed Reader",
                    "description": "Monitors RSS feed for new items",
                    "parameters": {
                        "url": "https://example.com/feed.xml"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "filter_new",
                    "type": "n8n-nodes-base.filter",
                    "name": "Filter New Items",
                    "description": "Filters for new items only",
                    "parameters": {},
                    "position": [450, 300]
                },
                {
                    "id": "save_data",
                    "type": "n8n-nodes-base.googleSheets",
                    "name": "Save to Sheets",
                    "description": "Saves new RSS items to Google Sheets",
                    "parameters": {
                        "operation": "append"
                    },
                    "position": [650, 300]
                }
            ],
            "connections": [
                {"from": "rss_trigger", "to": "filter_new", "output_index": 0, "input_index": 0},
                {"from": "filter_new", "to": "save_data", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "medium",
            "required_credentials": ["googleSheetsApi"]
        }
    
    def _create_file_plan(self, user_input: str) -> Dict[str, Any]:
        """Create file processing plan"""
        return {
            "workflow_name": f"File Processor: {user_input[:30]}...",
            "description": f"File processing workflow for: {user_input}",
            "nodes": [
                {
                    "id": "manual_trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "name": "Manual Trigger",
                    "description": "Start file processing",
                    "parameters": {},
                    "position": [250, 300]
                },
                {
                    "id": "read_file",
                    "type": "n8n-nodes-base.readBinaryFile",
                    "name": "Read File",
                    "description": "Read uploaded file",
                    "parameters": {},
                    "position": [450, 300]
                },
                {
                    "id": "process_csv",
                    "type": "n8n-nodes-base.spreadsheetFile",
                    "name": "Process CSV",
                    "description": "Parse and process CSV data",
                    "parameters": {
                        "operation": "read"
                    },
                    "position": [650, 300]
                }
            ],
            "connections": [
                {"from": "manual_trigger", "to": "read_file", "output_index": 0, "input_index": 0},
                {"from": "read_file", "to": "process_csv", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "medium",
            "required_credentials": []
        }
    
    def _create_email_plan(self, user_input: str) -> Dict[str, Any]:
        """Create email workflow plan"""
        return {
            "workflow_name": f"Email Workflow: {user_input[:30]}...",
            "description": f"Email-based workflow for: {user_input}",
            "nodes": [
                {
                    "id": "trigger",
                    "type": "n8n-nodes-base.manualTrigger",
                    "name": "Manual Trigger",
                    "description": "Start email workflow",
                    "parameters": {},
                    "position": [250, 300]
                },
                {
                    "id": "prepare_email",
                    "type": "n8n-nodes-base.code",
                    "name": "Prepare Email",
                    "description": "Prepare email content",
                    "parameters": {
                        "jsCode": "// Prepare email content\nreturn [{json: {to: 'user@example.com', subject: 'Notification', body: 'Your workflow has been triggered'}}];"
                    },
                    "position": [450, 300]
                },
                {
                    "id": "send_email",
                    "type": "n8n-nodes-base.emailSend",
                    "name": "Send Email",
                    "description": "Send email notification",
                    "parameters": {},
                    "position": [650, 300]
                }
            ],
            "connections": [
                {"from": "trigger", "to": "prepare_email", "output_index": 0, "input_index": 0},
                {"from": "prepare_email", "to": "send_email", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "low",
            "required_credentials": ["smtp"]
        }
    
    def _create_social_media_plan(self, user_input: str) -> Dict[str, Any]:
        """Create comprehensive social media automation plan"""
        return {
            "workflow_name": f"YouTube/Social Media Automation System",
            "description": f"Complete social media automation workflow for: {user_input}",
            "nodes": [
                {
                    "id": "schedule_trigger",
                    "type": "n8n-nodes-base.cron",
                    "name": "Content Schedule",
                    "description": "Triggers content creation and posting schedule",
                    "parameters": {
                        "rule": {
                            "interval": [{"field": "hour", "value": 9}, {"field": "minute", "value": 0}]
                        }
                    },
                    "position": [200, 200]
                },
                {
                    "id": "content_database",
                    "type": "n8n-nodes-base.googleSheets",
                    "name": "Content Database",
                    "description": "Fetches content ideas and scripts from database",
                    "parameters": {
                        "operation": "read",
                        "sheetId": "content_library",
                        "range": "A:J"
                    },
                    "position": [400, 200]
                },
                {
                    "id": "ai_content_generator",
                    "type": "n8n-nodes-base.openAi",
                    "name": "AI Content Generator",
                    "description": "Generates video scripts and descriptions using AI",
                    "parameters": {
                        "operation": "complete",
                        "model": "gpt-4",
                        "prompt": "Create engaging YouTube content based on: {{$json.topic}}"
                    },
                    "position": [600, 150]
                },
                {
                    "id": "thumbnail_generator",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Thumbnail Generator",
                    "description": "Creates custom thumbnails using AI image generation",
                    "parameters": {
                        "method": "POST",
                        "url": "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                        "headers": {
                            "Authorization": "Bearer {{$credentials.stabilityAi.apiKey}}"
                        }
                    },
                    "position": [600, 250]
                },
                {
                    "id": "video_processor",
                    "type": "n8n-nodes-base.code",
                    "name": "Video Processing",
                    "description": "Processes video metadata and optimization",
                    "parameters": {
                        "jsCode": "// Process video for different platforms\nconst platforms = ['youtube', 'tiktok', 'instagram', 'linkedin'];\nconst content = $json;\nconst results = [];\n\nplatforms.forEach(platform => {\n  const optimized = {\n    platform,\n    title: content.title.substring(0, platform === 'youtube' ? 100 : 60),\n    description: content.description,\n    tags: content.tags.slice(0, platform === 'youtube' ? 15 : 5),\n    thumbnail: content.thumbnail,\n    schedule_time: content.optimal_times[platform]\n  };\n  results.push({json: optimized});\n});\n\nreturn results;"
                    },
                    "position": [800, 200]
                },
                {
                    "id": "youtube_upload",
                    "type": "n8n-nodes-base.youTube",
                    "name": "YouTube Upload",
                    "description": "Uploads video to YouTube with metadata",
                    "parameters": {
                        "operation": "upload",
                        "title": "={{$json.title}}",
                        "description": "={{$json.description}}",
                        "tags": "={{$json.tags}}",
                        "categoryId": "22",
                        "privacy": "public"
                    },
                    "position": [1000, 100]
                },
                {
                    "id": "tiktok_upload",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "TikTok Upload",
                    "description": "Uploads content to TikTok",
                    "parameters": {
                        "method": "POST",
                        "url": "https://open-api.tiktok.com/share/video/upload/",
                        "headers": {
                            "Authorization": "Bearer {{$credentials.tiktok.accessToken}}"
                        }
                    },
                    "position": [1000, 200]
                },
                {
                    "id": "instagram_upload",
                    "type": "n8n-nodes-base.instagram",
                    "name": "Instagram Upload",
                    "description": "Posts to Instagram with hashtags",
                    "parameters": {
                        "operation": "post",
                        "type": "media",
                        "caption": "={{$json.description}} {{$json.tags.join(' ')}}"
                    },
                    "position": [1000, 300]
                },
                {
                    "id": "linkedin_post",
                    "type": "n8n-nodes-base.linkedIn",
                    "name": "LinkedIn Post",
                    "description": "Creates professional LinkedIn post",
                    "parameters": {
                        "operation": "create",
                        "text": "={{$json.description}}",
                        "visibility": "public"
                    },
                    "position": [1000, 400]
                },
                {
                    "id": "analytics_tracker",
                    "type": "n8n-nodes-base.googleAnalytics",
                    "name": "Analytics Tracker",
                    "description": "Tracks performance across all platforms",
                    "parameters": {
                        "operation": "report",
                        "reportType": "social_media_performance"
                    },
                    "position": [1200, 200]
                },
                {
                    "id": "performance_analyzer",
                    "type": "n8n-nodes-base.code",
                    "name": "Performance Analyzer",
                    "description": "Analyzes content performance and suggests improvements",
                    "parameters": {
                        "jsCode": "// Analyze performance metrics\nconst metrics = $json;\nconst analysis = {\n  engagement_rate: (metrics.likes + metrics.comments + metrics.shares) / metrics.views,\n  best_performing_time: metrics.peak_engagement_hour,\n  content_score: metrics.retention_rate * 100,\n  recommendations: []\n};\n\nif (analysis.engagement_rate < 0.03) {\n  analysis.recommendations.push('Improve thumbnail design');\n  analysis.recommendations.push('Optimize title for SEO');\n}\n\nif (metrics.retention_rate < 0.5) {\n  analysis.recommendations.push('Create more engaging openings');\n  analysis.recommendations.push('Improve content pacing');\n}\n\nreturn [{json: analysis}];"
                    },
                    "position": [1400, 150]
                },
                {
                    "id": "trend_analyzer",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Trend Analyzer",
                    "description": "Analyzes current trends and viral content",
                    "parameters": {
                        "method": "GET",
                        "url": "https://api.trending-topics.com/v1/trends",
                        "headers": {
                            "Authorization": "Bearer {{$credentials.trendingApi.key}}"
                        }
                    },
                    "position": [200, 400]
                },
                {
                    "id": "competitor_analysis",
                    "type": "n8n-nodes-base.code",
                    "name": "Competitor Analysis",
                    "description": "Analyzes competitor content and strategies",
                    "parameters": {
                        "jsCode": "// Analyze competitor performance\nconst competitors = ['competitor1', 'competitor2', 'competitor3'];\nconst analysis = [];\n\ncompetitors.forEach(comp => {\n  const data = {\n    name: comp,\n    avg_views: Math.floor(Math.random() * 100000) + 10000,\n    engagement_rate: (Math.random() * 0.1) + 0.02,\n    posting_frequency: Math.floor(Math.random() * 7) + 1,\n    top_content_types: ['tutorials', 'reviews', 'entertainment']\n  };\n  analysis.push(data);\n});\n\nreturn [{json: {competitor_analysis: analysis}}];"
                    },
                    "position": [400, 400]
                },
                {
                    "id": "seo_optimizer",
                    "type": "n8n-nodes-base.code",
                    "name": "SEO Optimizer",
                    "description": "Optimizes content for search and discovery",
                    "parameters": {
                        "jsCode": "// SEO optimization\nconst content = $json;\nconst keywords = content.trending_keywords || [];\nconst optimized = {\n  title: content.title,\n  description: content.description,\n  tags: [...content.tags, ...keywords.slice(0, 5)],\n  seo_score: 0\n};\n\n// Calculate SEO score\nif (optimized.title.length >= 60 && optimized.title.length <= 100) optimized.seo_score += 20;\nif (optimized.description.length >= 125) optimized.seo_score += 20;\nif (optimized.tags.length >= 10) optimized.seo_score += 20;\nif (keywords.some(k => optimized.title.toLowerCase().includes(k.toLowerCase()))) optimized.seo_score += 20;\nif (optimized.description.includes('subscribe')) optimized.seo_score += 20;\n\nreturn [{json: optimized}];"
                    },
                    "position": [600, 400]
                },
                {
                    "id": "audience_targeting",
                    "type": "n8n-nodes-base.googleAds",
                    "name": "Audience Targeting",
                    "description": "Creates targeted ad campaigns for content promotion",
                    "parameters": {
                        "operation": "createCampaign",
                        "campaignType": "video",
                        "targetAudience": "={{$json.demographics}}"
                    },
                    "position": [800, 400]
                },
                {
                    "id": "email_notification",
                    "type": "n8n-nodes-base.emailSend",
                    "name": "Team Notification",
                    "description": "Sends performance reports to team",
                    "parameters": {
                        "subject": "Daily Social Media Report - {{$now}}",
                        "text": "Content Performance Summary:\n\nVideos Published: {{$json.videos_published}}\nTotal Views: {{$json.total_views}}\nEngagement Rate: {{$json.avg_engagement}}%\n\nTop Performing Content:\n{{$json.top_content}}\n\nRecommendations:\n{{$json.recommendations.join('\n')}}"
                    },
                    "position": [1400, 300]
                },
                {
                    "id": "backup_storage",
                    "type": "n8n-nodes-base.googleDrive",
                    "name": "Content Backup",
                    "description": "Backs up all content and metadata to cloud storage",
                    "parameters": {
                        "operation": "upload",
                        "folderId": "backup_folder",
                        "fileName": "content_{{$now}}.json"
                    },
                    "position": [1200, 400]
                }
            ],
            "connections": [
                {"from": "schedule_trigger", "to": "content_database", "output_index": 0, "input_index": 0},
                {"from": "schedule_trigger", "to": "trend_analyzer", "output_index": 0, "input_index": 0},
                {"from": "content_database", "to": "ai_content_generator", "output_index": 0, "input_index": 0},
                {"from": "content_database", "to": "thumbnail_generator", "output_index": 0, "input_index": 0},
                {"from": "ai_content_generator", "to": "video_processor", "output_index": 0, "input_index": 0},
                {"from": "thumbnail_generator", "to": "video_processor", "output_index": 0, "input_index": 0},
                {"from": "video_processor", "to": "youtube_upload", "output_index": 0, "input_index": 0},
                {"from": "video_processor", "to": "tiktok_upload", "output_index": 0, "input_index": 0},
                {"from": "video_processor", "to": "instagram_upload", "output_index": 0, "input_index": 0},
                {"from": "video_processor", "to": "linkedin_post", "output_index": 0, "input_index": 0},
                {"from": "youtube_upload", "to": "analytics_tracker", "output_index": 0, "input_index": 0},
                {"from": "tiktok_upload", "to": "analytics_tracker", "output_index": 0, "input_index": 0},
                {"from": "instagram_upload", "to": "analytics_tracker", "output_index": 0, "input_index": 0},
                {"from": "linkedin_post", "to": "analytics_tracker", "output_index": 0, "input_index": 0},
                {"from": "analytics_tracker", "to": "performance_analyzer", "output_index": 0, "input_index": 0},
                {"from": "trend_analyzer", "to": "competitor_analysis", "output_index": 0, "input_index": 0},
                {"from": "competitor_analysis", "to": "seo_optimizer", "output_index": 0, "input_index": 0},
                {"from": "seo_optimizer", "to": "audience_targeting", "output_index": 0, "input_index": 0},
                {"from": "performance_analyzer", "to": "email_notification", "output_index": 0, "input_index": 0},
                {"from": "audience_targeting", "to": "backup_storage", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "enterprise",
            "required_credentials": ["youTubeApi", "tiktokApi", "instagramApi", "linkedInApi", "googleSheetsApi", "openAiApi", "stabilityAi", "googleAnalytics", "googleAds", "smtpEmail", "googleDriveApi"]
        }
    
    def _create_api_integration_plan(self, user_input: str) -> Dict[str, Any]:
        """Create API integration hub plan"""
        return {
            "workflow_name": f"API Integration Hub: {user_input[:30]}...",
            "description": f"API integration workflow for: {user_input}",
            "nodes": [
                {
                    "id": "webhook_trigger",
                    "type": "n8n-nodes-base.webhook",
                    "name": "API Trigger",
                    "description": "Receives integration requests",
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "integration-hub"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "github_sync",
                    "type": "n8n-nodes-base.github",
                    "name": "GitHub Sync",
                    "description": "Syncs with GitHub repositories",
                    "parameters": {
                        "operation": "getRepository"
                    },
                    "position": [450, 200]
                },
                {
                    "id": "jira_update",
                    "type": "n8n-nodes-base.jira",
                    "name": "Update Jira",
                    "description": "Updates Jira tickets",
                    "parameters": {
                        "operation": "update"
                    },
                    "position": [450, 300]
                },
                {
                    "id": "slack_notify",
                    "type": "n8n-nodes-base.slack",
                    "name": "Slack Notification",
                    "description": "Sends status updates to Slack",
                    "parameters": {
                        "operation": "postMessage",
                        "channel": "#integrations"
                    },
                    "position": [450, 400]
                },
                {
                    "id": "consolidate",
                    "type": "n8n-nodes-base.merge",
                    "name": "Consolidate Data",
                    "description": "Merges data from all sources",
                    "parameters": {},
                    "position": [650, 300]
                },
                {
                    "id": "error_handler",
                    "type": "n8n-nodes-base.code",
                    "name": "Error Handler",
                    "description": "Handles integration errors",
                    "parameters": {
                        "jsCode": "// Handle errors and retry logic\nif ($json.error) {\n  return [{json: {status: 'retry', message: $json.error}}];\n}\nreturn [{json: {status: 'success'}}];"
                    },
                    "position": [850, 300]
                }
            ],
            "connections": [
                {"from": "webhook_trigger", "to": "github_sync", "output_index": 0, "input_index": 0},
                {"from": "webhook_trigger", "to": "jira_update", "output_index": 0, "input_index": 0},
                {"from": "webhook_trigger", "to": "slack_notify", "output_index": 0, "input_index": 0},
                {"from": "github_sync", "to": "consolidate", "output_index": 0, "input_index": 0},
                {"from": "jira_update", "to": "consolidate", "output_index": 0, "input_index": 1},
                {"from": "slack_notify", "to": "consolidate", "output_index": 0, "input_index": 2},
                {"from": "consolidate", "to": "error_handler", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "high",
            "required_credentials": ["githubApi", "jiraApi", "slackApi"]
        }
    
    def _create_ecommerce_plan(self, user_input: str) -> Dict[str, Any]:
        """Create e-commerce automation plan"""
        return {
            "workflow_name": f"E-commerce Automation: {user_input[:30]}...",
            "description": f"E-commerce workflow for: {user_input}",
            "nodes": [
                {
                    "id": "order_webhook",
                    "type": "n8n-nodes-base.webhook",
                    "name": "New Order Trigger",
                    "description": "Triggered when new order is placed",
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "new-order"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "validate_inventory",
                    "type": "n8n-nodes-base.code",
                    "name": "Validate Inventory",
                    "description": "Checks product availability",
                    "parameters": {
                        "jsCode": "// Check inventory levels\nconst order = $json;\nconst available = order.quantity <= 100; // Mock check\nreturn [{json: {...order, available}}];"
                    },
                    "position": [450, 250]
                },
                {
                    "id": "process_payment",
                    "type": "n8n-nodes-base.stripe",
                    "name": "Process Payment",
                    "description": "Processes payment via Stripe",
                    "parameters": {
                        "operation": "createCharge"
                    },
                    "position": [450, 350]
                },
                {
                    "id": "update_database",
                    "type": "n8n-nodes-base.postgres",
                    "name": "Update Database",
                    "description": "Updates order in database",
                    "parameters": {
                        "operation": "insert"
                    },
                    "position": [650, 200]
                },
                {
                    "id": "send_confirmation",
                    "type": "n8n-nodes-base.emailSend",
                    "name": "Order Confirmation",
                    "description": "Sends confirmation email",
                    "parameters": {
                        "subject": "Order Confirmation #{{$json.orderId}}"
                    },
                    "position": [650, 300]
                },
                {
                    "id": "fulfill_order",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Trigger Fulfillment",
                    "description": "Triggers warehouse fulfillment",
                    "parameters": {
                        "method": "POST",
                        "url": "https://warehouse-api.example.com/fulfill"
                    },
                    "position": [650, 400]
                },
                {
                    "id": "analytics_update",
                    "type": "n8n-nodes-base.googleSheets",
                    "name": "Update Analytics",
                    "description": "Updates business analytics",
                    "parameters": {
                        "operation": "append"
                    },
                    "position": [850, 300]
                }
            ],
            "connections": [
                {"from": "order_webhook", "to": "validate_inventory", "output_index": 0, "input_index": 0},
                {"from": "order_webhook", "to": "process_payment", "output_index": 0, "input_index": 0},
                {"from": "validate_inventory", "to": "update_database", "output_index": 0, "input_index": 0},
                {"from": "process_payment", "to": "send_confirmation", "output_index": 0, "input_index": 0},
                {"from": "send_confirmation", "to": "fulfill_order", "output_index": 0, "input_index": 0},
                {"from": "fulfill_order", "to": "analytics_update", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "high",
            "required_credentials": ["stripeApi", "postgresDb", "smtpEmail", "googleSheetsApi"]
        }
    
    def _create_testing_plan(self, user_input: str) -> Dict[str, Any]:
        """Create testing automation plan"""
        return {
            "workflow_name": f"Testing Automation: {user_input[:30]}...",
            "description": f"Testing automation workflow for: {user_input}",
            "nodes": [
                {
                    "id": "code_trigger",
                    "type": "n8n-nodes-base.github",
                    "name": "Code Change Trigger",
                    "description": "Triggered by code commits",
                    "parameters": {
                        "event": "push"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "run_unit_tests",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Run Unit Tests",
                    "description": "Executes unit test suite",
                    "parameters": {
                        "method": "POST",
                        "url": "https://ci-server.example.com/run-tests",
                        "jsonParameters": true,
                        "options": {
                            "bodyParametersUi": {
                                "parameter": [
                                    {"name": "test_type", "value": "unit"},
                                    {"name": "branch", "value": "={{$json.branch}}"}
                                ]
                            }
                        }
                    },
                    "position": [450, 200]
                },
                {
                    "id": "run_integration_tests",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Run Integration Tests",
                    "description": "Executes integration tests",
                    "parameters": {
                        "method": "POST",
                        "url": "https://ci-server.example.com/run-tests",
                        "jsonParameters": true,
                        "options": {
                            "bodyParametersUi": {
                                "parameter": [
                                    {"name": "test_type", "value": "integration"},
                                    {"name": "branch", "value": "={{$json.branch}}"}
                                ]
                            }
                        }
                    },
                    "position": [450, 300]
                },
                {
                    "id": "quality_check",
                    "type": "n8n-nodes-base.code",
                    "name": "Quality Analysis",
                    "description": "Analyzes code quality metrics",
                    "parameters": {
                        "jsCode": "// Analyze test results\nconst unitResults = $input.first().json;\nconst integrationResults = $input.last().json;\nconst passed = unitResults.passed && integrationResults.passed;\nreturn [{json: {passed, coverage: unitResults.coverage, quality: passed ? 'high' : 'needs_work'}}];"
                    },
                    "position": [650, 250]
                },
                {
                    "id": "notify_team",
                    "type": "n8n-nodes-base.slack",
                    "name": "Notify Team",
                    "description": "Sends test results to team",
                    "parameters": {
                        "operation": "postMessage",
                        "channel": "#dev-team",
                        "text": "Test Results: {{$json.passed ? '✅ PASSED' : '❌ FAILED'}} - Coverage: {{$json.coverage}}%"
                    },
                    "position": [850, 200]
                },
                {
                    "id": "create_report",
                    "type": "n8n-nodes-base.googleSheets",
                    "name": "Test Report",
                    "description": "Creates detailed test report",
                    "parameters": {
                        "operation": "append"
                    },
                    "position": [850, 300]
                }
            ],
            "connections": [
                {"from": "code_trigger", "to": "run_unit_tests", "output_index": 0, "input_index": 0},
                {"from": "code_trigger", "to": "run_integration_tests", "output_index": 0, "input_index": 0},
                {"from": "run_unit_tests", "to": "quality_check", "output_index": 0, "input_index": 0},
                {"from": "run_integration_tests", "to": "quality_check", "output_index": 0, "input_index": 0},
                {"from": "quality_check", "to": "notify_team", "output_index": 0, "input_index": 0},
                {"from": "quality_check", "to": "create_report", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "high",
            "required_credentials": ["githubApi", "slackApi", "googleSheetsApi"]
        }
    
    def _create_developer_plan(self, user_input: str) -> Dict[str, Any]:
        """Create developer automation plan"""
        return {
            "workflow_name": f"Developer Automation: {user_input[:30]}...",
            "description": f"Developer workflow for: {user_input}",
            "nodes": [
                {
                    "id": "pull_request_trigger",
                    "type": "n8n-nodes-base.github",
                    "name": "PR Trigger",
                    "description": "Triggered by pull requests",
                    "parameters": {
                        "event": "pull_request"
                    },
                    "position": [250, 300]
                },
                {
                    "id": "code_review",
                    "type": "n8n-nodes-base.code",
                    "name": "Automated Code Review",
                    "description": "Performs automated code analysis",
                    "parameters": {
                        "jsCode": "// Simulate code review\nconst pr = $json;\nconst issues = [\n  {type: 'style', severity: 'minor', message: 'Consider using const instead of let'},\n  {type: 'security', severity: 'major', message: 'Potential SQL injection vulnerability'}\n];\nreturn [{json: {pr_id: pr.id, issues, approved: issues.filter(i => i.severity === 'major').length === 0}}];"
                    },
                    "position": [450, 250]
                },
                {
                    "id": "run_build",
                    "type": "n8n-nodes-base.httpRequest",
                    "name": "Build & Deploy",
                    "description": "Triggers CI/CD pipeline",
                    "parameters": {
                        "method": "POST",
                        "url": "https://ci.example.com/build",
                        "jsonParameters": true
                    },
                    "position": [450, 350]
                },
                {
                    "id": "update_pr",
                    "type": "n8n-nodes-base.github",
                    "name": "Update PR Status",
                    "description": "Updates PR with review results",
                    "parameters": {
                        "operation": "createReview"
                    },
                    "position": [650, 250]
                },
                {
                    "id": "notify_developer",
                    "type": "n8n-nodes-base.slack",
                    "name": "Notify Developer",
                    "description": "Notifies developer of results",
                    "parameters": {
                        "operation": "postMessage",
                        "text": "PR Review Complete: {{$json.approved ? '✅ Approved' : '❌ Needs Changes'}}"
                    },
                    "position": [650, 350]
                },
                {
                    "id": "auto_merge",
                    "type": "n8n-nodes-base.github",
                    "name": "Auto Merge",
                    "description": "Automatically merges if approved",
                    "parameters": {
                        "operation": "merge"
                    },
                    "position": [850, 300]
                }
            ],
            "connections": [
                {"from": "pull_request_trigger", "to": "code_review", "output_index": 0, "input_index": 0},
                {"from": "pull_request_trigger", "to": "run_build", "output_index": 0, "input_index": 0},
                {"from": "code_review", "to": "update_pr", "output_index": 0, "input_index": 0},
                {"from": "run_build", "to": "notify_developer", "output_index": 0, "input_index": 0},
                {"from": "update_pr", "to": "auto_merge", "output_index": 0, "input_index": 0}
            ],
            "estimated_complexity": "high",
            "required_credentials": ["githubApi", "slackApi"]
        }
    
    def _create_intelligent_generic_plan(self, user_input: str) -> Dict[str, Any]:
        """Create intelligent generic plan based on input analysis"""
        # Analyze input for complexity and create appropriate workflow
        word_count = len(user_input.split())
        
        if word_count > 20:  # Complex request
            return {
                "workflow_name": f"Complex Workflow: {user_input[:40]}...",
                "description": f"Multi-stage workflow for: {user_input}",
                "nodes": [
                    {
                        "id": "trigger",
                        "type": "n8n-nodes-base.manualTrigger",
                        "name": "Start Workflow",
                        "description": "Initiates the workflow",
                        "parameters": {},
                        "position": [250, 300]
                    },
                    {
                        "id": "data_input",
                        "type": "n8n-nodes-base.code",
                        "name": "Data Processing",
                        "description": "Processes input data",
                        "parameters": {
                            "jsCode": f"// Processing for: {user_input[:100]}\nconst processedData = {{\n  input: '{user_input}',\n  timestamp: new Date().toISOString(),\n  status: 'processing'\n}};\nreturn [{{json: processedData}}];"
                        },
                        "position": [450, 250]
                    },
                    {
                        "id": "validation",
                        "type": "n8n-nodes-base.code",
                        "name": "Data Validation",
                        "description": "Validates processed data",
                        "parameters": {
                            "jsCode": "// Validate data quality\nconst data = $json;\nconst isValid = data.input && data.input.length > 10;\nreturn [{json: {...data, validated: isValid}}];"
                        },
                        "position": [650, 200]
                    },
                    {
                        "id": "transformation",
                        "type": "n8n-nodes-base.code",
                        "name": "Data Transformation",
                        "description": "Transforms data for output",
                        "parameters": {
                            "jsCode": "// Transform data\nconst data = $json;\nconst transformed = {\n  ...data,\n  processed: true,\n  output_format: 'json',\n  complexity: 'high'\n};\nreturn [{json: transformed}];"
                        },
                        "position": [450, 350]
                    },
                    {
                        "id": "notification",
                        "type": "n8n-nodes-base.emailSend",
                        "name": "Send Notification",
                        "description": "Sends completion notification",
                        "parameters": {
                            "subject": "Workflow Completed",
                            "text": "Your complex workflow has been completed successfully."
                        },
                        "position": [850, 300]
                    }
                ],
                "connections": [
                    {"from": "trigger", "to": "data_input", "output_index": 0, "input_index": 0},
                    {"from": "data_input", "to": "validation", "output_index": 0, "input_index": 0},
                    {"from": "data_input", "to": "transformation", "output_index": 0, "input_index": 0},
                    {"from": "validation", "to": "notification", "output_index": 0, "input_index": 0},
                    {"from": "transformation", "to": "notification", "output_index": 0, "input_index": 0}
                ],
                "estimated_complexity": "high",
                "required_credentials": ["smtpEmail"]
            }
        else:  # Simple request
            return {
                "workflow_name": f"Simple Workflow: {user_input[:40]}...",
                "description": f"Basic workflow for: {user_input}",
                "nodes": [
                    {
                        "id": "start",
                        "type": "n8n-nodes-base.manualTrigger",
                        "name": "Manual Trigger",
                        "description": "Starts the workflow",
                        "parameters": {},
                        "position": [250, 300]
                    },
                    {
                        "id": "process",
                        "type": "n8n-nodes-base.code",
                        "name": "Process Request",
                        "description": "Processes the request",
                        "parameters": {
                            "jsCode": f"// Processing for: {user_input}\nconst result = {{\n  request: '{user_input}',\n  processed_at: new Date().toISOString(),\n  status: 'completed'\n}};\nreturn [{{json: result}}];"
                        },
                        "position": [450, 300]
                    },
                    {
                        "id": "output",
                        "type": "n8n-nodes-base.code",
                        "name": "Format Output",
                        "description": "Formats the final output",
                        "parameters": {
                            "jsCode": "// Format output\nconst data = $json;\nreturn [{json: {...data, formatted: true}}];"
                        },
                        "position": [650, 300]
                    }
                ],
                "connections": [
                    {"from": "start", "to": "process", "output_index": 0, "input_index": 0},
                    {"from": "process", "to": "output", "output_index": 0, "input_index": 0}
                ],
                "estimated_complexity": "low",
                "required_credentials": []
            }
    
    def _get_timestamp(self) -> str:
        from datetime import datetime
        return datetime.now().isoformat()
    
    async def run(self, message: Message) -> Message:
        """Main run method for ADK compatibility"""
        input_data = json.loads(message.content)
        user_input = input_data.get("cleaned_input", input_data.get("original_input", ""))
        
        plan = await self.plan_workflow(user_input)
        
        return Message(
            content=json.dumps(plan),
            sender=self.name,
            metadata={"planned": True}
        )