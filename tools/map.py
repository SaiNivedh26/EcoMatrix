"""
Location detection and mapping tool for EcoMatrix Agent
Handles location queries and finds nearby shops/services
"""

import math
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from config import Config

logger = logging.getLogger(__name__)

class LocationTool:
    """Tool for handling location detection and nearby place searches"""
    
    def __init__(self):
        self.locations = Config.LOCATIONS
        self.service_area = Config.DEFAULT_AREA
        
        logger.info(f"🗺️ LocationTool initialized with {len(self.locations)} locations")
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        try:
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lng = math.radians(lng2 - lng1)
            
            a = (math.sin(delta_lat/2)**2 + 
                 math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            
            return R * c
            
        except Exception as e:
            logger.error(f"❌ Error calculating distance: {e}")
            return float('inf')
    
    def is_within_service_area(self, lat: float, lng: float) -> bool:
        """Check if coordinates are within the service area bounds"""
        try:
            bounds = self.service_area["bounds"]
            return (bounds["south"] <= lat <= bounds["north"] and
                    bounds["west"] <= lng <= bounds["east"])
        except Exception as e:
            logger.error(f"❌ Error checking service area: {e}")
            return False
    
    async def find_nearby_locations(self, user_lat: float, user_lng: float, query: str = "") -> Dict[str, Any]:
        """
        Find nearby locations based on user coordinates and query.
        This is the main endpoint that the agent will call.
        """
        try:
            logger.info(f"🔍 Finding locations near ({user_lat:.4f}, {user_lng:.4f}) for query: '{query}'")
            
            # Check if user is within service area
            if not self.is_within_service_area(user_lat, user_lng):
                return {
                    "error": "Location is outside the service area",
                    "service_area": self.service_area["bounds"],
                    "user_location": {"lat": user_lat, "lng": user_lng},
                    "message": "I'm sorry, but you're outside our service area. We currently serve the downtown area."
                }
            
            # Calculate distances to all locations
            locations_with_distance = []
            for location in self.locations:
                try:
                    distance = self.calculate_distance(
                        user_lat, user_lng, 
                        location['lat'], location['lng']
                    )
                    
                    location_copy = location.copy()
                    location_copy['distance'] = round(distance, 3)
                    locations_with_distance.append(location_copy)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing location {location.get('name', 'unknown')}: {e}")
                    continue
            
            # Sort by distance
            locations_with_distance.sort(key=lambda x: x.get('distance', float('inf')))
            
            # Filter by query if provided
            filtered_locations = self._filter_by_query(locations_with_distance, query)
            
            # Get top 5 results
            nearest_locations = filtered_locations[:5]
            
            # Generate conversational response
            response_message = self._generate_location_response(nearest_locations, query)
            
            result = {
                "user_location": {"lat": user_lat, "lng": user_lng},
                "nearest_locations": nearest_locations,
                "total_found": len(filtered_locations),
                "query": query,
                "message": response_message,
                "service_area": self.service_area["bounds"],
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Found {len(nearest_locations)} locations for user")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error finding nearby locations: {e}")
            return {
                "error": str(e),
                "message": "I'm sorry, I'm having trouble finding locations right now. Please try again."
            }
    
    def _filter_by_query(self, locations: List[Dict], query: str) -> List[Dict]:
        """Filter locations based on the user's query"""
        if not query or query.strip() == "":
            return locations
        
        query_lower = query.lower()
        filtered = []
        
        # Define keywords for different types of places
        keywords_map = {
            "coffee": ["coffee", "cafe", "espresso", "latte"],
            "hardware": ["hardware", "tools", "hammer", "equipment", "repair"],
            "books": ["book", "library", "reading", "magazine", "stationery"],
            "tech": ["tech", "electronics", "computer", "gadget", "phone"],
            "house": ["house", "home", "residential", "apartment"],
            "shop": ["shop", "store", "market", "retail"]
        }
        
        # Score each location based on relevance to query
        for location in locations:
            score = 0
            location_text = f"{location['name']} {location['description']} {location['type']}".lower()
            
            # Direct keyword matches
            for category, keywords in keywords_map.items():
                for keyword in keywords:
                    if keyword in query_lower:
                        if keyword in location_text or category in location_text:
                            score += 10
                        elif location['type'] == category or category in location['name'].lower():
                            score += 5
            
            # General relevance
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:  # Ignore very short words
                    if word in location_text:
                        score += 3
            
            # Type matching
            if any(word in location['type'].lower() for word in query_words):
                score += 5
            
            location['relevance_score'] = score
            
            # Include if score > 0 or if no specific query filtering needed
            if score > 0 or len(query_words) <= 2:
                filtered.append(location)
        
        # Sort by relevance score (descending) then by distance (ascending)
        filtered.sort(key=lambda x: (-x.get('relevance_score', 0), x.get('distance', float('inf'))))
        
        logger.info(f"🔍 Filtered {len(locations)} locations to {len(filtered)} based on query: '{query}'")
        return filtered
    
    def _generate_location_response(self, locations: List[Dict], query: str) -> str:
        """Generate a conversational response about the locations found"""
        try:
            if not locations:
                if query:
                    return f"I didn't find any {query} in your immediate area. Would you like me to help you find something else?"
                else:
                    return "I don't see any places in your immediate area right now. Could you try a different location or tell me what you're looking for?"
            
            if len(locations) == 1:
                loc = locations[0]
                distance_text = f"{loc['distance']:.1f} kilometers" if loc['distance'] < 1 else f"{loc['distance']:.1f} km"
                return f"I found {loc['name']} about {distance_text} from you. {loc.get('description', '')} Would you like directions or more information?"
            
            # Multiple locations
            response_parts = []
            
            if query:
                response_parts.append(f"I found several options for {query} near you!")
            else:
                response_parts.append("Here are some places near you!")
            
            # Mention the closest 2-3 locations
            for i, loc in enumerate(locations[:3]):
                distance_text = f"{loc['distance']:.1f} km" if loc['distance'] >= 1 else f"{int(loc['distance']*1000)} meters"
                
                if i == 0:
                    response_parts.append(f"The closest is {loc['name']}, just {distance_text} away.")
                elif i == 1:
                    response_parts.append(f"There's also {loc['name']} at {distance_text}.")
                else:
                    response_parts.append(f"And {loc['name']} is {distance_text} from you.")
            
            if len(locations) > 3:
                response_parts.append(f"I found {len(locations) - 3} more options as well.")
            
            response_parts.append("Which one sounds interesting, or would you like more details about any of them?")
            
            return " ".join(response_parts)
            
        except Exception as e:
            logger.error(f"❌ Error generating location response: {e}")
            return "I found some locations near you, but I'm having trouble describing them right now. Would you like me to try again?"
    
    async def get_location_details(self, location_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific location"""
        try:
            for location in self.locations:
                if location.get('id') == location_id:
                    return {
                        **location,
                        "detailed_info": self._get_detailed_location_info(location),
                        "timestamp": datetime.now().isoformat()
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting location details: {e}")
            return None
    
    def _get_detailed_location_info(self, location: Dict[str, Any]) -> str:
        """Generate detailed information about a location for voice response"""
        try:
            info_parts = [location.get('description', '')]
            
            # Add type-specific information
            location_type = location.get('type', '').lower()
            
            if location_type == 'shop':
                if 'coffee' in location['name'].lower():
                    info_parts.append("They serve freshly brewed coffee and have a cozy atmosphere.")
                elif 'hardware' in location['name'].lower() or 'hammer' in location['name'].lower():
                    info_parts.append("You can find tools, equipment, and hardware supplies there.")
                elif 'book' in location['name'].lower():
                    info_parts.append("They have a wide selection of books and reading materials.")
                elif 'tech' in location['name'].lower():
                    info_parts.append("They specialize in electronics and the latest gadgets.")
                else:
                    info_parts.append("It's a local shop with friendly service.")
            
            elif location_type == 'house':
                info_parts.append("This is a residential property in the area.")
            
            # Add general location context
            info_parts.append("It's located in our downtown service area with easy access.")
            
            return " ".join(filter(None, info_parts))
            
        except Exception as e:
            logger.error(f"❌ Error generating detailed info: {e}")
            return location.get('description', 'A local business in the area.')
    
    def get_service_area_info(self) -> Dict[str, Any]:
        """Get information about the service area"""
        return {
            "area": self.service_area,
            "total_locations": len(self.locations),
            "location_types": list(set(loc.get('type', 'unknown') for loc in self.locations)),
            "message": "We serve the downtown area with various shops and services."
        }
    
    async def detect_user_intent(self, query: str) -> Dict[str, Any]:
        """Detect what the user is looking for based on their query"""
        try:
            query_lower = query.lower()
            
            intent_data = {
                "query": query,
                "detected_intents": [],
                "suggested_searches": [],
                "confidence": 0.0
            }
            
            # Define intent patterns
            intent_patterns = {
                "find_coffee": ["coffee", "cafe", "espresso", "latte", "cappuccino"],
                "find_hardware": ["hardware", "tools", "hammer", "screwdriver", "repair"],
                "find_books": ["book", "library", "reading", "novel", "magazine"],
                "find_tech": ["tech", "electronics", "computer", "phone", "gadget"],
                "find_food": ["restaurant", "food", "eat", "hungry", "meal"],
                "general_search": ["shop", "store", "near", "nearby", "find", "looking"]
            }
            
            # Check for intent matches
            for intent, keywords in intent_patterns.items():
                matches = sum(1 for keyword in keywords if keyword in query_lower)
                if matches > 0:
                    confidence = min(matches / len(keywords), 1.0)
                    intent_data["detected_intents"].append({
                        "intent": intent,
                        "confidence": confidence,
                        "matched_keywords": [kw for kw in keywords if kw in query_lower]
                    })
            
            # Sort by confidence
            intent_data["detected_intents"].sort(key=lambda x: x["confidence"], reverse=True)
            
            # Set overall confidence
            if intent_data["detected_intents"]:
                intent_data["confidence"] = intent_data["detected_intents"][0]["confidence"]
            
            # Generate suggestions
            if intent_data["confidence"] > 0.3:
                top_intent = intent_data["detected_intents"][0]["intent"]
                if "coffee" in top_intent:
                    intent_data["suggested_searches"] = ["coffee shops", "cafes", "places for drinks"]
                elif "hardware" in top_intent:
                    intent_data["suggested_searches"] = ["hardware stores", "tool shops", "repair services"]
                elif "books" in top_intent:
                    intent_data["suggested_searches"] = ["bookstores", "libraries", "reading places"]
                elif "tech" in top_intent:
                    intent_data["suggested_searches"] = ["electronics stores", "computer shops", "tech services"]
                else:
                    intent_data["suggested_searches"] = ["nearby shops", "local businesses", "services"]
            
            return intent_data
            
        except Exception as e:
            logger.error(f"❌ Error detecting user intent: {e}")
            return {
                "query": query,
                "detected_intents": [],
                "suggested_searches": ["nearby places"],
                "confidence": 0.0,
                "error": str(e)
            }

