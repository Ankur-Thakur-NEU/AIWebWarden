#!/usr/bin/env python3
"""
Multi-Modal AI Agent Enhancement
Adds image analysis, document processing, and multimedia content handling
"""

import base64
import requests
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import mimetypes
from cerebras_client import get_completion
from tools import web_search, scrape_url

class MultiModalAgent:
    """Enhanced agent with multi-modal capabilities."""
    
    def __init__(self, model_name: str = "llama3.1-8b"):
        """Initialize multi-modal agent."""
        self.model_name = model_name
        self.supported_formats = {
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'documents': ['.pdf', '.docx', '.txt', '.md', '.rtf'],
            'web_content': ['text/html', 'application/json', 'text/xml']
        }
        
    def analyze_image_from_url(self, image_url: str, query: str = "") -> str:
        """Analyze an image from URL and provide insights."""
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                return f"Error: URL does not point to an image (content-type: {content_type})"
            
            # Encode image to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            
            # Create analysis prompt
            analysis_prompt = f"""
You are analyzing an image from the URL: {image_url}

User Query: {query if query else "Describe what you see in this image"}

Based on the image content, provide a detailed analysis including:
1. Main subjects and objects visible
2. Setting/environment
3. Colors, composition, and style
4. Any text or readable content
5. Context and potential significance
6. Answer to the user's specific query if provided

Since I cannot directly process images, I'll provide guidance on what to look for and suggest web searches for similar content analysis.
"""
            
            # Get text-based analysis guidance
            guidance = get_completion(analysis_prompt, model=self.model_name, max_tokens=400)
            
            # Search for similar content or context
            search_query = f"image analysis {query}" if query else "image content analysis techniques"
            search_results = web_search(search_query, max_results=3)
            
            return f"""🖼️ IMAGE ANALYSIS for {image_url}

📋 Analysis Guidance:
{guidance}

🔍 Related Information:
{search_results}

💡 Note: For detailed image analysis, consider using specialized computer vision APIs like Google Vision API, AWS Rekognition, or Azure Computer Vision.
"""
            
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
    
    def process_document_content(self, content: str, content_type: str, query: str = "") -> str:
        """Process document content with AI analysis."""
        try:
            # Truncate very long content
            if len(content) > 5000:
                content = content[:5000] + "... [truncated]"
            
            analysis_prompt = f"""
Analyze the following document content and respond to the user's query.

Document Type: {content_type}
User Query: {query if query else "Summarize and analyze this document"}

Document Content:
{content}

Provide a comprehensive analysis including:
1. Main topics and themes
2. Key information and insights
3. Structure and organization
4. Important details relevant to the query
5. Summary and conclusions
"""
            
            analysis = get_completion(analysis_prompt, model=self.model_name, max_tokens=600)
            
            return f"""📄 DOCUMENT ANALYSIS

📊 Content Type: {content_type}
📝 Length: {len(content)} characters

🧠 AI Analysis:
{analysis}
"""
            
        except Exception as e:
            return f"Error processing document: {str(e)}"
    
    def enhanced_web_scraping(self, url: str, query: str = "") -> str:
        """Enhanced web scraping with content type detection and processing."""
        try:
            # First, get basic page info
            response = requests.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            # Handle different content types
            if 'image' in content_type:
                return self.analyze_image_from_url(url, query)
            
            elif 'pdf' in content_type:
                return f"""📄 PDF Document Detected: {url}

💡 PDF Processing Recommendation:
For comprehensive PDF analysis, consider using:
- PyPDF2 or pdfplumber for text extraction
- Specialized document AI services
- OCR tools for scanned documents

🔍 Alternative: Searching for information about this document...
{web_search(f"PDF document analysis {query}", max_results=3)}
"""
            
            else:
                # Regular web scraping with enhanced analysis
                scraped_content = scrape_url(url)
                
                if query:
                    # Analyze scraped content in context of query
                    analysis_prompt = f"""
Based on the following web content from {url}, answer the user's query: "{query}"

Web Content:
{scraped_content[:3000]}

Provide a focused response that:
1. Directly addresses the user's query
2. Cites relevant information from the page
3. Provides additional context if helpful
4. Mentions the source URL
"""
                    
                    analysis = get_completion(analysis_prompt, model=self.model_name, max_tokens=500)
                    
                    return f"""🌐 ENHANCED WEB ANALYSIS for {url}

❓ Query: {query}

🎯 Focused Response:
{analysis}

📄 Source Content Preview:
{scraped_content[:500]}...
"""
                else:
                    return scraped_content
                    
        except Exception as e:
            return f"Error in enhanced web scraping: {str(e)}"
    
    def multimedia_query_processor(self, query: str) -> str:
        """Process queries that might involve multimedia content."""
        query_lower = query.lower()
        
        # Detect multimedia-related queries
        multimedia_keywords = {
            'image': ['image', 'picture', 'photo', 'screenshot', 'diagram', 'chart'],
            'video': ['video', 'youtube', 'movie', 'clip', 'recording'],
            'audio': ['audio', 'music', 'podcast', 'sound', 'recording'],
            'document': ['pdf', 'document', 'paper', 'report', 'file']
        }
        
        detected_types = []
        for media_type, keywords in multimedia_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_types.append(media_type)
        
        if detected_types:
            # Enhanced search with multimedia focus
            search_results = web_search(query, max_results=5)
            
            # Provide multimedia-specific guidance
            multimedia_guidance = self._get_multimedia_guidance(detected_types)
            
            return f"""🎭 MULTIMEDIA-ENHANCED RESPONSE

🔍 Search Results:
{search_results}

🎯 Multimedia Processing Guidance:
{multimedia_guidance}

💡 For direct multimedia processing, consider:
- Image analysis: Google Vision API, AWS Rekognition
- Video analysis: YouTube API, video processing libraries
- Audio analysis: Speech-to-text services, audio analysis APIs
- Document processing: OCR services, document AI platforms
"""
        else:
            # Regular query processing
            return web_search(query, max_results=5)
    
    def _get_multimedia_guidance(self, media_types: List[str]) -> str:
        """Get specific guidance for multimedia content types."""
        guidance = []
        
        if 'image' in media_types:
            guidance.append("🖼️ Images: Look for visual content, infographics, charts, and diagrams")
        
        if 'video' in media_types:
            guidance.append("🎥 Videos: Search for tutorials, demonstrations, and visual explanations")
        
        if 'audio' in media_types:
            guidance.append("🎵 Audio: Consider podcasts, interviews, and audio explanations")
        
        if 'document' in media_types:
            guidance.append("📄 Documents: Look for PDFs, research papers, and detailed reports")
        
        return "\n".join(guidance)
    
    def smart_content_router(self, query: str, content_url: Optional[str] = None) -> str:
        """Intelligently route queries based on content type and query nature."""
        if content_url:
            # Direct content analysis
            return self.enhanced_web_scraping(content_url, query)
        else:
            # Query-based routing
            return self.multimedia_query_processor(query)

class EnhancedMultiModalInterface:
    """Enhanced interface with multi-modal capabilities."""
    
    def __init__(self):
        """Initialize enhanced interface."""
        self.agent = MultiModalAgent()
        self.session_history = []
    
    def process_enhanced_query(self, query: str, attachments: List[str] = None) -> Dict[str, Any]:
        """Process query with potential multimedia attachments."""
        result = {
            'query': query,
            'response': '',
            'multimedia_processed': [],
            'suggestions': []
        }
        
        try:
            if attachments:
                # Process each attachment
                multimedia_results = []
                for attachment in attachments:
                    if attachment.startswith('http'):
                        # URL attachment
                        mm_result = self.agent.enhanced_web_scraping(attachment, query)
                        multimedia_results.append(f"📎 {attachment}:\n{mm_result}")
                        result['multimedia_processed'].append(attachment)
                
                # Combine results
                if multimedia_results:
                    result['response'] = "\n\n".join(multimedia_results)
                else:
                    result['response'] = self.agent.smart_content_router(query)
            else:
                # Regular enhanced query
                result['response'] = self.agent.smart_content_router(query)
            
            # Add suggestions for multimedia enhancement
            result['suggestions'] = self._generate_multimedia_suggestions(query)
            
            # Store in session history
            self.session_history.append(result)
            
            return result
            
        except Exception as e:
            result['response'] = f"Error processing enhanced query: {str(e)}"
            return result
    
    def _generate_multimedia_suggestions(self, query: str) -> List[str]:
        """Generate suggestions for multimedia enhancement."""
        suggestions = []
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['how to', 'tutorial', 'guide']):
            suggestions.append("🎥 Try searching for video tutorials on this topic")
        
        if any(word in query_lower for word in ['compare', 'vs', 'difference']):
            suggestions.append("📊 Look for comparison charts or infographics")
        
        if any(word in query_lower for word in ['data', 'statistics', 'numbers']):
            suggestions.append("📈 Search for data visualizations and charts")
        
        if any(word in query_lower for word in ['example', 'sample', 'demo']):
            suggestions.append("🖼️ Look for visual examples and screenshots")
        
        return suggestions

# Demo function
def demo_multimodal_capabilities():
    """Demonstrate multi-modal capabilities."""
    print("🎭 MULTI-MODAL AI AGENT DEMO")
    print("="*50)
    
    interface = EnhancedMultiModalInterface()
    
    # Test queries
    test_cases = [
        {
            'query': "How to create a Python web application?",
            'attachments': None,
            'description': "Regular query with multimedia suggestions"
        },
        {
            'query': "Analyze this image for me",
            'attachments': ["https://example.com/sample-image.jpg"],
            'description': "Image analysis query"
        },
        {
            'query': "What are the latest AI developments?",
            'attachments': None,
            'description': "Enhanced web search"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        if test_case['attachments']:
            print(f"Attachments: {test_case['attachments']}")
        print("-" * 60)
        
        result = interface.process_enhanced_query(
            test_case['query'], 
            test_case['attachments']
        )
        
        print(f"✅ Response generated ({len(result['response'])} chars)")
        if result['multimedia_processed']:
            print(f"🎭 Multimedia processed: {len(result['multimedia_processed'])} items")
        if result['suggestions']:
            print(f"💡 Suggestions: {len(result['suggestions'])} provided")
        
        print(f"Preview: {result['response'][:200]}...")

if __name__ == "__main__":
    demo_multimodal_capabilities()
