import requests
from typing import Dict, List, Tuple
import time
from config import Config

class ListingsAuditor:
    """Audit business listings across multiple platforms"""
    
    def __init__(self, config: Config):
        self.config = config
        self.google_api_key = config.GOOGLE_PLACES_API_KEY
        self.yelp_api_key = config.YELP_API_KEY
        self.facebook_token = config.FACEBOOK_ACCESS_TOKEN
    
    def audit_business(self, business_name: str, zip_code: str, address: str = None) -> Dict:
        """
        Perform comprehensive audit across all platforms
        
        Args:
            business_name: Name of the business
            zip_code: ZIP code of the business
            address: Optional full address
            
        Returns:
            Dictionary containing audit results for all platforms
        """
        results = {
            'business_name': business_name,
            'zip_code': zip_code,
            'overall_score': 0,
            'platforms': {},
            'issues': [],
            'recommendations': [],
            'timestamp': time.time()
        }
        
        # Audit Google My Business
        google_results = self.audit_google(business_name, zip_code, address)
        results['platforms']['google'] = google_results
        
        # Audit Yelp
        yelp_results = self.audit_yelp(business_name, zip_code)
        results['platforms']['yelp'] = yelp_results
        
        # Audit Facebook
        facebook_results = self.audit_facebook(business_name, zip_code)
        results['platforms']['facebook'] = facebook_results
        
        # Calculate overall score and compile issues
        results['overall_score'] = self._calculate_overall_score(results['platforms'])
        results['issues'] = self._compile_issues(results['platforms'])
        results['recommendations'] = self._generate_recommendations(results['platforms'])
        
        return results
    
    def audit_google(self, business_name: str, zip_code: str, address: str = None) -> Dict:
        """Audit Google My Business listing"""
        result = {
            'platform': 'Google My Business',
            'is_listed': False,
            'is_claimed': False,
            'has_correct_info': False,
            'has_photos': False,
            'has_reviews': False,
            'review_count': 0,
            'average_rating': 0.0,
            'issues': [],
            'score': 0
        }
        
        if not self.google_api_key:
            result['issues'].append('Google Places API key not configured')
            return result
        
        try:
            # Search for business using Google Places API
            search_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json'
            params = {
                'input': f"{business_name} {zip_code}",
                'inputtype': 'textquery',
                'fields': 'place_id,name,formatted_address,rating,user_ratings_total,photos,business_status',
                'key': self.google_api_key
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK' and data.get('candidates'):
                place = data['candidates'][0]
                result['is_listed'] = True
                result['has_correct_info'] = True  # Simplified check
                
                # Get detailed information
                if 'place_id' in place:
                    details = self._get_google_place_details(place['place_id'])
                    if details:
                        result['is_claimed'] = details.get('business_status') == 'OPERATIONAL'
                        result['has_photos'] = len(details.get('photos', [])) > 0
                        result['has_reviews'] = details.get('user_ratings_total', 0) > 0
                        result['review_count'] = details.get('user_ratings_total', 0)
                        result['average_rating'] = details.get('rating', 0.0)
                
                # Check for issues
                if not result['is_claimed']:
                    result['issues'].append('Business listing not claimed')
                if not result['has_photos']:
                    result['issues'].append('No photos uploaded')
                if result['review_count'] < 5:
                    result['issues'].append('Insufficient reviews (less than 5)')
                if not place.get('formatted_address'):
                    result['issues'].append('Address information incomplete')
            else:
                result['issues'].append('Business not found on Google')
            
            # Calculate score
            result['score'] = self._calculate_platform_score(result)
            
        except Exception as e:
            result['issues'].append(f'Error checking Google: {str(e)}')
        
        return result
    
    def _get_google_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a Google place"""
        try:
            details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,photos,business_status,opening_hours',
                'key': self.google_api_key
            }
            
            response = requests.get(details_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('result', {})
        except Exception:
            pass
        
        return {}
    
    def audit_yelp(self, business_name: str, zip_code: str) -> Dict:
        """Audit Yelp listing"""
        result = {
            'platform': 'Yelp',
            'is_listed': False,
            'is_claimed': False,
            'has_correct_info': False,
            'has_photos': False,
            'has_reviews': False,
            'review_count': 0,
            'average_rating': 0.0,
            'issues': [],
            'score': 0
        }
        
        if not self.yelp_api_key:
            result['issues'].append('Yelp API key not configured')
            return result
        
        try:
            # Search for business using Yelp Fusion API
            search_url = 'https://api.yelp.com/v3/businesses/search'
            headers = {'Authorization': f'Bearer {self.yelp_api_key}'}
            params = {
                'term': business_name,
                'location': zip_code,
                'limit': 1
            }
            
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            data = response.json()
            
            if data.get('businesses'):
                business = data['businesses'][0]
                result['is_listed'] = True
                result['is_claimed'] = not business.get('is_closed', False)
                result['has_photos'] = len(business.get('photos', [])) > 0
                result['has_reviews'] = business.get('review_count', 0) > 0
                result['review_count'] = business.get('review_count', 0)
                result['average_rating'] = business.get('rating', 0.0)
                result['has_correct_info'] = True  # Simplified
                
                # Check for issues
                if business.get('is_closed'):
                    result['issues'].append('Business marked as closed')
                if not result['has_photos']:
                    result['issues'].append('No photos on Yelp')
                if result['review_count'] < 3:
                    result['issues'].append('Few reviews on Yelp')
            else:
                result['issues'].append('Business not found on Yelp')
            
            result['score'] = self._calculate_platform_score(result)
            
        except Exception as e:
            result['issues'].append(f'Error checking Yelp: {str(e)}')
        
        return result
    
    def audit_facebook(self, business_name: str, zip_code: str) -> Dict:
        """Audit Facebook Business Page"""
        result = {
            'platform': 'Facebook',
            'is_listed': False,
            'is_claimed': False,
            'has_correct_info': False,
            'has_photos': False,
            'has_reviews': False,
            'review_count': 0,
            'average_rating': 0.0,
            'issues': [],
            'score': 0
        }
        
        if not self.facebook_token:
            result['issues'].append('Facebook API token not configured')
            return result
        
        try:
            # Note: Facebook Graph API search requires specific permissions
            # This is a simplified implementation
            search_url = 'https://graph.facebook.com/v18.0/pages/search'
            params = {
                'q': business_name,
                'type': 'place',
                'center': f'{zip_code}',
                'access_token': self.facebook_token
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            data = response.json()
            
            if data.get('data'):
                page = data['data'][0]
                result['is_listed'] = True
                result['is_claimed'] = True  # If found, likely claimed
                result['has_photos'] = 'cover' in page or 'picture' in page
                
                # Get additional details if page ID available
                if 'id' in page:
                    page_details = self._get_facebook_page_details(page['id'])
                    if page_details:
                        result['has_reviews'] = page_details.get('rating_count', 0) > 0
                        result['review_count'] = page_details.get('rating_count', 0)
                        result['average_rating'] = page_details.get('overall_star_rating', 0.0)
                
                # Check for issues
                if not result['has_photos']:
                    result['issues'].append('No profile/cover photo on Facebook')
                if result['review_count'] < 3:
                    result['issues'].append('Few reviews on Facebook')
            else:
                result['issues'].append('Business not found on Facebook')
            
            result['score'] = self._calculate_platform_score(result)
            
        except Exception as e:
            result['issues'].append(f'Error checking Facebook: {str(e)}')
        
        return result
    
    def _get_facebook_page_details(self, page_id: str) -> Dict:
        """Get detailed Facebook page information"""
        try:
            details_url = f'https://graph.facebook.com/v18.0/{page_id}'
            params = {
                'fields': 'name,rating_count,overall_star_rating,phone,website,about',
                'access_token': self.facebook_token
            }
            
            response = requests.get(details_url, params=params, timeout=10)
            return response.json()
        except Exception:
            pass
        
        return {}
    
    def _calculate_platform_score(self, platform_result: Dict) -> int:
        """Calculate score for a single platform (0-100)"""
        score = 0
        
        if platform_result['is_listed']:
            score += 30
        if platform_result['is_claimed']:
            score += 20
        if platform_result['has_correct_info']:
            score += 15
        if platform_result['has_photos']:
            score += 15
        if platform_result['has_reviews']:
            score += 10
        if platform_result['review_count'] >= 5:
            score += 10
        
        return min(score, 100)
    
    def _calculate_overall_score(self, platforms: Dict) -> int:
        """Calculate overall audit score across all platforms"""
        scores = [p['score'] for p in platforms.values() if 'score' in p]
        return int(sum(scores) / len(scores)) if scores else 0
    
    def _compile_issues(self, platforms: Dict) -> List[str]:
        """Compile all issues from all platforms"""
        all_issues = []
        for platform_name, platform_data in platforms.items():
            for issue in platform_data.get('issues', []):
                all_issues.append(f"{platform_data['platform']}: {issue}")
        return all_issues
    
    def _generate_recommendations(self, platforms: Dict) -> List[str]:
        """Generate actionable recommendations based on audit results"""
        recommendations = []
        
        for platform_name, platform_data in platforms.items():
            platform = platform_data['platform']
            
            if not platform_data['is_listed']:
                recommendations.append(f"Create a business listing on {platform}")
            elif not platform_data['is_claimed']:
                recommendations.append(f"Claim your business listing on {platform}")
            
            if not platform_data['has_photos']:
                recommendations.append(f"Add high-quality photos to your {platform} listing")
            
            if platform_data['review_count'] < 5:
                recommendations.append(f"Encourage customers to leave reviews on {platform}")
            
            if not platform_data['has_correct_info']:
                recommendations.append(f"Update business information on {platform}")
        
        # General recommendations
        if len(recommendations) > 5:
            recommendations.append("Consider professional online presence management to address all issues")
        
        return recommendations
