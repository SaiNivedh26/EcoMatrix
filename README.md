# EcoGram Bharat: AI-Powered Waste Management Ecosystem

<img width="512" height="128" alt="image" src="https://github.com/user-attachments/assets/30429389-c6a2-4a6b-9a01-d945a5c0c8d8" />


- EcoGram Bharat is an innovative platform developed by Team EcoMatrix for the ICSRF 2025 Hackathon final round.
- Designed to tackle rural waste management challenges in India, it transforms waste into valuable resources through AI-driven insights, community sharing, and gamification. Like a community hub that turns trash into treasure—similar to how apps like OLX connect buyers and sellers but tailored for sustainability—EcoGram Bharat empowers users to identify, reuse, and share materials effortlessly.
- While focused on rural areas, the system is adaptable for urban settings, making it versatile for any city or village.

---

## What It Does ??
<br>

EcoGram Bharat addresses waste management by integrating AI, mapping, and accessible interfaces, drawing inspiration from real-world tools like recycling apps and community marketplaces:

1. AI Material Identification: Snap a photo to identify waste types and get DIY reuse suggestions using vision models like LLaVA and Gemini.
2. Geo-Mapping for Resources: Real-time interactive maps (via Google Maps SDK) to locate and share materials, report garbage dumps, and optimize collection routes.
3. Gamification and Rewards: Earn points for eco-friendly actions, redeemable for subsidies, discounts, or welfare priorities to boost participation.
4. Voice Agent for Inclusivity: A Sarvam AI-powered multi-lingual voice agent allows users, especially the elderly or those without smartphones, to call a number for insights on nearby materials, garbage reporting, or leaderboard updates—ensuring accessibility without tech barriers.
5. Community Resource Sharing: Connect users for trading or sharing waste-derived resources like compost or upcycled items.
6. Government Data Insights: Conversational access to waste trends and impacts via integrated datasets.



## Voice Interaction (Core Idea)

Users can dial a Twilio-allocated number to interact with the voice agent, which provides multi-lingual guidance on material reuse, nearby resources, or reporting issues.
In the app, use voice commands for hands-free operation.

## Configuration
EcoGram Bharat is configured for rural India but can be adapted to any location by updating geo-bounds and datasets in the backend. It supports multiple Indian languages via Sarvam.ai, frontier Indian Model service provider and integrates with government APIs for real-time data.


## Pipeline
<img width="729" height="895" alt="image" src="https://github.com/user-attachments/assets/ed1f69cd-aee5-40ae-854f-68b13e35afdb" />

## Tech Stacks
- React Native & Expo: Cross-platform mobile app development.
- FastAPI: High-performance backend for AI and voice endpoints.
- Flask: Handles basic CRUD and web interfaces.
- Google Maps SDK & Folium: Interactive mapping.
- LLaVA & Gemini (Google GenAI): Vision and contextual AI processing.
- Sarvam.ai: Multi-lingual language detection, routing, and voice support.
- Twilio & ElevenLabs: Phone call integration and natural speech output.
- MongoDB: Real-time data storage for materials and users.
- Azure Blob Storage: Image handling.
- Hugging Face Models: Embeddings and vision models.
- LangChain, Groq LLM, & LangGraph: Conversational AI and agent workflows.
- Qdrant: Vector storage for government data.
- Tavily & Scrapegraph AI: Web scraping for DIY guides.
- Appwrite: Authentication.
- LangSmith: Model monitoring.
- Flask-CORS: Cross-origin support.

<br>

## Troubleshooting
### Encountering issues? Here's how to resolve common ones:

- Voice Agent Problems: Verify Twilio setup and Sarvam.ai API keys; ensure language support is configured.
- AI Identification Errors: Check image quality and Gemini/Hugging Face API keys in .env.
- Map Not Loading: Confirm Google Maps API key and internet connectivity.
- Database Issues: Ensure MongoDB connection strings are correct.

## Status
Code cleaning and testing are in progress to refine performance and ensure reliability.

License
EcoGram Bharat is licensed under the MIT License. Feel free to use, modify, or contribute.


## 👥 Contributors

Thanks to all the amazing people who contributed to this project 💚

- [Sai Nivedh](https://github.com/SaiNivedh26)  
- [Hari Heman](https://github.com/HXMAN76)  
- [Roshan](https://github.com/Twinn-github09)  
- [Thrishala](https://github.com/thrishalasivakumar)  
- [Mokitha](https://github.com/Mokitha-Sakthi)  
- [Hygrevan](https://github.com/Hygrevan-343)

