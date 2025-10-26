#!/usr/bin/env python3
"""
Comprehensive QA Testing Script for Moving.to
Automatically detects common issues in city pages
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def check_template_variables(content: str) -> List[str]:
    """Check for unreplaced template variables"""
    return re.findall(r'\{\{[A-Z_]+\}\}', content)

def check_generic_placeholders(content: str) -> List[str]:
    """Check for generic placeholder text"""
    issues = []
    
    # Check for generic climate/currency/language
    if 'Local Time' in content and 'Time Zone' in content:
        issues.append("Generic 'Local Time' placeholder found")
    if 'Local Language' in content:
        issues.append("Generic 'Local Language' placeholder found")
    if 'Local Currency' in content:
        issues.append("Generic 'Local Currency' placeholder found")
    
    return issues

def check_broken_links(content: str, city_name: str) -> List[str]:
    """Check for broken or malformed links"""
    issues = []
    
    # Check LLM-optimized link
    if 'LLM-Optimized Version' in content:
        # Check if it has a proper href
        llm_link_match = re.search(r'<a[^>]*>LLM-Optimized Version</a>', content)
        if llm_link_match:
            link_text = llm_link_match.group(0)
            if 'href=""' in link_text or 'href="()"' in link_text:
                issues.append("LLM-Optimized link is empty/broken")
    
    # Check Airbnb links
    airbnb_matches = re.findall(r'href="([^"]*airbnb[^"]*)"', content, re.IGNORECASE)
    for link in airbnb_matches:
        if not link or link == '()' or '{{' in link:
            issues.append(f"Broken Airbnb link: {link}")
    
    # Check accommodation links
    if 'Find Accommodation' in content or 'Browse All Listings' in content:
        accom_match = re.search(r'(Find Accommodation|Browse All Listings)[^<]*<a[^>]*href="([^"]*)"', content)
        if accom_match and (not accom_match.group(2) or accom_match.group(2) == '()'):
            issues.append("Accommodation link is empty/broken")
    
    return issues

def check_navigation_menu(content: str) -> List[str]:
    """Check for navigation menu elements"""
    issues = []
    
    required_nav = [
        ('Home button', r'<a[^>]*>Home</a>'),
        ('Navigation menu', r'<nav|<div[^>]*class="[^"]*nav'),
    ]
    
    for name, pattern in required_nav:
        if not re.search(pattern, content, re.IGNORECASE):
            issues.append(f"Missing {name}")
    
    return issues

def check_collapsible_sections(content: str) -> List[str]:
    """Check if data sections are collapsible"""
    issues = []
    
    # Check if there are collapsible elements for listings
    if 'rental' in content.lower() or 'listing' in content.lower():
        if not re.search(r'(collaps|expand|toggle|accordion)', content, re.IGNORECASE):
            issues.append("Rental listings should be in collapsible sections")
    
    return issues

def check_real_data_previews(content: str) -> List[str]:
    """Check if page has real data previews (not just links)"""
    issues = []
    
    # Check if external links have preview data
    external_services = ['airbnb', 'zillow', 'indeed', 'tripadvisor']
    
    for service in external_services:
        if service in content.lower():
            # Check if there's actual preview data nearby (not just a link)
            service_section = re.search(
                f'({service}.*?)(?:<section|<div class="section"|$)', 
                content, 
                re.IGNORECASE | re.DOTALL
            )
            if service_section:
                section_text = service_section.group(1)
                # Check if section has actual data (prices, titles, etc.)
                has_data = bool(re.search(r'\$\d+|bed|bath|rating', section_text, re.IGNORECASE))
                if not has_data:
                    issues.append(f"{service.title()} section has no preview data")
    
    return issues

def check_neighborhoods(content: str, city_name: str) -> List[str]:
    """Check if neighborhoods are city-specific or generic"""
    issues = []
    
    # Generic neighborhood names that appear in every city
    generic_neighborhoods = ['Downtown', 'Suburbs', 'Historic District']
    
    neighborhood_section = re.search(
        r'(Popular Neighborhoods|Neighborhoods).*?(?=<section|<div class="section"|$)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    
    if neighborhood_section:
        section_text = neighborhood_section.group(0)
        # Count how many generic names appear
        generic_count = sum(1 for name in generic_neighborhoods if name in section_text)
        
        if generic_count >= 2:
            issues.append(f"Neighborhoods appear generic (found {generic_count}/3 generic names)")
    
    return issues

def run_qa_on_city(city_data: Dict, base_dir: Path) -> Tuple[str, List[str]]:
    """Run all QA checks on a single city"""
    city_name = city_data.get('name', 'Unknown')
    country = city_data.get('country', 'Unknown')
    
    # Build file path
    country_slug = slugify(country)
    state_slug = slugify(city_data.get('state', city_name))
    city_slug = slugify(city_name)
    
    file_path = base_dir / country_slug / state_slug / city_slug / 'index.html'
    
    if not file_path.exists():
        return f"{city_name}, {country}", [f"File not found: {file_path}"]
    
    # Read content
    content = file_path.read_text(encoding='utf-8')
    
    # Run all checks
    all_issues = []
    
    # 1. Template variables
    template_vars = check_template_variables(content)
    if template_vars:
        all_issues.append(f"❌ Template variables: {list(set(template_vars))[:3]}")
    
    # 2. Generic placeholders
    generic_issues = check_generic_placeholders(content)
    all_issues.extend([f"❌ {issue}" for issue in generic_issues])
    
    # 3. Broken links
    link_issues = check_broken_links(content, city_name)
    all_issues.extend([f"❌ {issue}" for issue in link_issues])
    
    # 4. Navigation
    nav_issues = check_navigation_menu(content)
    all_issues.extend([f"⚠️  {issue}" for issue in nav_issues])
    
    # 5. Collapsible sections
    collapse_issues = check_collapsible_sections(content)
    all_issues.extend([f"⚠️  {issue}" for issue in collapse_issues])
    
    # 6. Real data previews
    preview_issues = check_real_data_previews(content)
    all_issues.extend([f"⚠️  {issue}" for issue in preview_issues])
    
    # 7. Generic neighborhoods
    neighborhood_issues = check_neighborhoods(content, city_name)
    all_issues.extend([f"⚠️  {issue}" for issue in neighborhood_issues])
    
    return f"{city_name}, {country}", all_issues

def main():
    """Main QA function"""
    base_dir = Path('/home/ubuntu/moving_to_world')
    
    # Load database
    database_file = base_dir / 'city-database.json'
    with open(database_file, 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    # Test cities (diverse sample)
    test_cities = [
        ('Paris', 'France'),
        ('Tel Aviv', 'Israel'),
        ('Tokyo', 'Japan'),
        ('London', 'United Kingdom'),
        ('New York', 'United States'),
        ('Sydney', 'Australia'),
        ('Netanya', 'Israel'),
    ]
    
    print("="*80)
    print("COMPREHENSIVE QA TEST - Moving.to")
    print("="*80)
    print()
    
    total_issues = 0
    cities_with_issues = 0
    
    for city_name, country_name in test_cities:
        # Find city in database
        city_data = None
        for city in cities:
            if city.get('name', '').lower() == city_name.lower() and city.get('country') == country_name:
                city_data = city
                break
        
        if not city_data:
            print(f"❌ {city_name}, {country_name} - NOT FOUND in database")
            continue
        
        # Run QA
        city_label, issues = run_qa_on_city(city_data, base_dir)
        
        if issues:
            print(f"\n{'❌' if any('❌' in i for i in issues) else '⚠️ '} {city_label}")
            for issue in issues:
                print(f"   {issue}")
            total_issues += len(issues)
            cities_with_issues += 1
        else:
            print(f"\n✅ {city_label} - All checks passed!")
    
    # Summary
    print("\n" + "="*80)
    print("QA SUMMARY")
    print("="*80)
    print(f"Cities tested: {len(test_cities)}")
    print(f"Cities with issues: {cities_with_issues}")
    print(f"Total issues found: {total_issues}")
    
    if cities_with_issues == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {cities_with_issues} cities need attention")
    
    print("="*80)

if __name__ == '__main__':
    main()

