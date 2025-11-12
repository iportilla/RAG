"""
Streamlit Search UI for Azure AI Search - Hotels Dataset
Based on: https://learn.microsoft.com/en-us/azure/search/search-get-started-portal
Enhanced with Keyword, Semantic, and Semantic + Filters search modes
"""

import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    QueryType, 
    QueryCaptionType, 
    QueryAnswerType,
    VectorizedQuery
)
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Azure Search Configuration
SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY", "")
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "hotels-sample-index")
SEMANTIC_CONFIG_NAME = os.getenv("AZURE_SEARCH_SEMANTIC_CONFIG", "my-semantic-config")

def initialize_search_client():
    """Initialize Azure Search client"""
    if not SEARCH_SERVICE_ENDPOINT or not SEARCH_API_KEY:
        st.error("⚠️ Please configure Azure Search credentials in .env file")
        st.stop()
    
    try:
        credential = AzureKeyCredential(SEARCH_API_KEY)
        search_client = SearchClient(
            endpoint=SEARCH_SERVICE_ENDPOINT,
            index_name=SEARCH_INDEX_NAME,
            credential=credential
        )
        return search_client
    except Exception as e:
        st.error(f"Failed to initialize search client: {str(e)}")
        st.stop()

def perform_search(search_client, search_text, search_mode="keyword", filters=None, top=10):
    """
    Perform search on Azure Search index with different modes
    
    Args:
        search_client: Azure SearchClient instance
        search_text: Search query text
        search_mode: Search mode - "keyword", "semantic", or "semantic_filter"
        filters: OData filter expression
        top: Number of results to return
    """
    try:
        # Build base search parameters
        search_params = {
            "search_text": search_text if search_text else "*",
            "select": [
                "HotelId", "HotelName", "Description", "Category", 
                "Tags", "ParkingIncluded", "LastRenovationDate", 
                "Rating", "Address"
            ],
            "top": top,
            "include_total_count": True
        }
        
        # Configure based on search mode
        if search_mode == "semantic" or search_mode == "semantic_filter":
            # Semantic search configuration
            search_params["query_type"] = QueryType.SEMANTIC
            search_params["semantic_configuration_name"] = SEMANTIC_CONFIG_NAME
            search_params["query_caption"] = QueryCaptionType.EXTRACTIVE
            search_params["query_answer"] = QueryAnswerType.EXTRACTIVE
            
            # Add filter for semantic_filter mode
            if search_mode == "semantic_filter" and filters:
                search_params["filter"] = filters
        else:
            # Keyword search (default)
            search_params["query_type"] = QueryType.SIMPLE
            
            # Don't specify search_fields - let Azure Search use default searchable fields
            # This avoids errors if specific fields aren't marked as searchable
            # Azure Search will automatically search all fields marked as "Searchable" in the index
            
            # Add filter if provided
            if filters:
                search_params["filter"] = filters
        
        # Execute search
        results = search_client.search(**search_params)
        
        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        if "semantic" in str(e).lower():
            st.info("💡 If you see a semantic configuration error, your index may not have semantic search enabled. Try 'Keyword' mode instead.")
        else:
            st.info(f"💡 Search parameters used: Query='{search_text}', Mode={search_mode}, Filters={filters}")
        return None

def format_address(address):
    """Format hotel address for display"""
    if not address:
        return "N/A"
    
    parts = []
    if address.get("StreetAddress"):
        parts.append(address["StreetAddress"])
    if address.get("City"):
        parts.append(address["City"])
    if address.get("StateProvince"):
        parts.append(address["StateProvince"])
    if address.get("PostalCode"):
        parts.append(address["PostalCode"])
    
    return ", ".join(parts) if parts else "N/A"

def display_hotel_card(hotel, show_score=False, search_mode="keyword"):
    """Display hotel information in a card format"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Hotel name with search score badge
            hotel_name = hotel.get('HotelName', 'Unknown Hotel')
            if show_score and hasattr(hotel, '@search.score'):
                score = getattr(hotel, '@search.score', 0)
                st.markdown(f"### 🏨 {hotel_name} `Score: {score:.2f}`")
            else:
                st.markdown(f"### 🏨 {hotel_name}")
            
            # Show reranker score for semantic search
            if search_mode in ["semantic", "semantic_filter"] and hasattr(hotel, '@search.reranker_score'):
                reranker_score = getattr(hotel, '@search.reranker_score', 0)
                st.markdown(f"🎯 **Semantic Relevance Score:** `{reranker_score:.3f}`")
            
            # Category and Tags
            category = hotel.get('Category', 'N/A')
            st.markdown(f"**Category:** {category}")
            
            tags = hotel.get('Tags', [])
            if tags:
                tags_str = " • ".join([f"`{tag}`" for tag in tags])
                st.markdown(f"**Tags:** {tags_str}")
            
            # Show captions for semantic search
            if search_mode in ["semantic", "semantic_filter"] and hasattr(hotel, '@search.captions'):
                captions = getattr(hotel, '@search.captions', [])
                if captions:
                    st.markdown("**📝 Relevant Excerpt:**")
                    for caption in captions[:1]:  # Show first caption
                        caption_text = caption.text if hasattr(caption, 'text') else str(caption)
                        st.markdown(f"> {caption_text}")
            
            # Description
            description = hotel.get('Description', 'No description available')
            with st.expander("📖 Full Description", expanded=False):
                st.markdown(description)
            
            # Address
            address = format_address(hotel.get('Address', {}))
            st.markdown(f"📍 **Address:** {address}")
            
        with col2:
            # Rating
            rating = hotel.get('Rating')
            if rating:
                st.metric("⭐ Rating", f"{rating}/5")
            
            # Parking
            parking = hotel.get('ParkingIncluded')
            if parking:
                st.success("🅿️ Parking")
            
            # Last Renovation
            renovation = hotel.get('LastRenovationDate')
            if renovation:
                st.info(f"🔧 Renovated: {renovation[:4]}")
        
        st.divider()

def main():
    # Page configuration
    st.set_page_config(
        page_title="Azure AI Search - Hotels Demo",
        page_icon="🏨",
        layout="wide"
    )
    
    # Initialize session state for auto-search
    if 'last_search_params' not in st.session_state:
        st.session_state.last_search_params = None
    
    # Header
    st.title("🏨 Azure AI Search - Hotels Search Demo")
    st.markdown("""
    Search through a collection of 50 fictitious hotels using **Azure AI Search**.  
    This demo showcases keyword search, semantic search, and advanced filtering capabilities.
    """)
    
    # Initialize search client
    search_client = initialize_search_client()
    
    # Search Mode Selection (prominent position)
    st.markdown("### 🔎 Search Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_mode = st.selectbox(
            "Search Mode",
            options=["keyword", "semantic", "semantic_filter"],
            format_func=lambda x: {
                "keyword": "🔤 Keyword Search - Traditional full-text search",
                "semantic": "🧠 Semantic Search - AI-powered understanding",
                "semantic_filter": "🎯 Semantic + Filters - Best of both worlds"
            }[x],
            help="Choose your search mode"
        )
    
    with col2:
        show_scores = st.checkbox(
            "Show Relevance Scores",
            value=True,
            help="Display search and reranker scores"
        )
    
    # Display mode-specific info
    if search_mode == "keyword":
        st.info("💡 **Keyword Search**: Traditional BM25 ranking based on term frequency and document relevance.")
    elif search_mode == "semantic":
        st.info("🧠 **Semantic Search**: Uses AI to understand query intent and meaning. Provides captions and reranker scores. Filters are disabled in pure semantic mode.")
    else:
        st.info("🎯 **Semantic + Filters**: Combines semantic understanding with traditional filters for precise results.")
    
    # Search box
    search_query = st.text_input(
        "Search for hotels",
        placeholder="e.g., romantic getaway near the ocean, business hotel with conference rooms...",
        help="Enter your search query - semantic search understands natural language!"
    )
    
    # Sidebar for filters
    st.sidebar.header("⚙️ Search Configuration")
    
    # Filters in sidebar (disabled for pure semantic search)
    filters_enabled = search_mode != "semantic"
    
    st.sidebar.subheader("🎚️ Filters")
    
    if not filters_enabled:
        st.sidebar.warning("⚠️ Filters are disabled in pure Semantic Search mode. Use 'Semantic + Filters' to enable filters.")
    
    # Rating filter
    min_rating = st.sidebar.slider(
        "Minimum Rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5,
        help="Filter hotels by minimum rating",
        disabled=not filters_enabled
    )
    
    # Parking filter
    parking_filter = st.sidebar.checkbox(
        "Parking Included",
        help="Show only hotels with parking",
        disabled=not filters_enabled
    )
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Categories",
        options=["Budget", "Boutique", "Luxury", "Resort", "Suite"],
        help="Filter by hotel category",
        disabled=not filters_enabled
    )
    
    # Number of results
    top_results = st.sidebar.slider(
        "Number of results",
        min_value=5,
        max_value=50,
        value=10,
        step=5
    )
    
    # Advanced options
    with st.sidebar.expander("🔧 Advanced Options"):
        debug_mode = st.checkbox("Show debug info", help="Display search parameters and field information")
        
        if debug_mode:
            st.markdown("""
            **Search behavior:**
            - Searches ALL fields marked as 'Searchable' in your index
            - Common searchable fields: Description, Tags, Category
            - The app does NOT limit which fields are searched
            """)
            st.caption("💡 Azure Search automatically uses all searchable fields defined in your index schema.")
    
    # Build filter expression
    filter_expressions = []
    
    if filters_enabled:
        if min_rating > 1.0:
            filter_expressions.append(f"Rating ge {min_rating}")
        
        if parking_filter:
            filter_expressions.append("ParkingIncluded eq true")
        
        if categories:
            category_filters = " or ".join([f"Category eq '{cat}'" for cat in categories])
            filter_expressions.append(f"({category_filters})")
    
    filter_string = " and ".join(filter_expressions) if filter_expressions else None
    
    # Create search params tuple for comparison
    current_search_params = (search_query, search_mode, filter_string, top_results)
    
    # Auto-search toggle
    col_btn, col_auto = st.columns([3, 2])
    with col_btn:
        search_clicked = st.button("🔎 Search", type="primary", use_container_width=True)
    with col_auto:
        auto_search = st.checkbox("🔄 Auto-search", value=True, help="Automatically search when filters or mode changes")
    
    # Create search params tuple for comparison
    params_changed = st.session_state.last_search_params != current_search_params
    
    # Determine if we should search:
    # 1. Button was clicked
    # 2. Auto-search is on AND parameters changed AND (there's a query or filters)
    should_search = (
        search_clicked or 
        (auto_search and params_changed and (bool(search_query) or bool(filter_string)))
    )
    
    if should_search:
        # Update last search params
        st.session_state.last_search_params = current_search_params
        
        # Show indicator if auto-search triggered (not button click)
        if not search_clicked and auto_search:
            st.info("🔄 Auto-search triggered by filter/mode change")
        
        # Show debug info if enabled
        if debug_mode:
            st.markdown("### 🐛 Debug Information")
            debug_info = {
                "Search Query": search_query or "*",
                "Search Mode": search_mode,
                "Filter Expression": filter_string or "None",
                "Top Results": top_results,
                "Fields Searched": "All fields marked as 'Searchable' in your Azure Search index (default behavior)"
            }
            st.json(debug_info)
        
        with st.spinner(f"Searching hotels using {search_mode.replace('_', ' ').title()} mode..."):
            results = perform_search(
                search_client,
                search_query,
                search_mode=search_mode,
                filters=filter_string,
                top=top_results
            )
            
            if results:
                # Get total count
                total_count = results.get_count()
                
                # Display results count with mode indicator
                mode_emoji = {"keyword": "🔤", "semantic": "🧠", "semantic_filter": "🎯"}
                st.success(f"{mode_emoji.get(search_mode, '🔍')} Found **{total_count}** hotels using **{search_mode.replace('_', ' ').title()}** mode")
                
                # Show semantic answers if available
                if search_mode in ["semantic", "semantic_filter"]:
                    if hasattr(results, 'get_answers') and results.get_answers():
                        answers = results.get_answers()
                        if answers:
                            st.markdown("### 💬 AI-Generated Answer")
                            for answer in answers[:1]:  # Show first answer
                                answer_text = answer.text if hasattr(answer, 'text') else str(answer)
                                st.success(answer_text)
                
                # Convert results to list
                hotels = list(results)
                
                if hotels:
                    st.markdown("---")
                    st.markdown("### 🏨 Search Results")
                    
                    # Display each hotel
                    for idx, hotel in enumerate(hotels, 1):
                        st.markdown(f"**Result #{idx}**")
                        display_hotel_card(hotel, show_score=show_scores, search_mode=search_mode)
                else:
                    st.warning("❌ No hotels found matching your search criteria.")
                    st.markdown("### 💡 Troubleshooting Tips:")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("""
                        **Try these adjustments:**
                        - ✓ Remove or lower the rating filter
                        - ✓ Uncheck "Parking Included"
                        - ✓ Clear category filters
                        - ✓ Try simpler search terms
                        - ✓ Use different search mode
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Current search:**
                        - Query: `{search_query or 'Empty (showing all)'}`
                        - Mode: `{search_mode}`
                        - Min Rating: `{min_rating}`
                        - Parking Required: `{parking_filter}`
                        - Categories: `{categories if categories else 'None'}`
                        """)
                    
                    st.info("🔍 **Search Tip**: The search looks in all fields marked as 'Searchable' in your Azure Search index. Common searchable fields include Description, Tags, and Category. If you're not finding expected results, the term may not exist in your data, or the relevant fields may not be marked as searchable.")
    else:
        # Show welcome message
        if auto_search:
            st.info("👆 Enter a search query or apply filters - results will update automatically")
        else:
            st.info("👆 Enter a search query or apply filters, then click 🔎 Search")
        
        # Show example searches based on mode
        st.markdown("### 💡 Example Searches")
        
        if search_mode == "keyword":
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                **By Keyword:**
                - `beach`
                - `spa`
                - `luxury`
                - `historic`
                """)
            
            with col2:
                st.markdown("""
                **By Feature:**
                - `pool`
                - `wifi`
                - `restaurant`
                - `business center`
                """)
            
            with col3:
                st.markdown("""
                **By Location:**
                - `Seattle`
                - `San Francisco`
                - `New York`
                - `Miami`
                """)
        else:
            # Semantic search examples
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                **Natural Language Queries:**
                - `romantic getaway near the ocean`
                - `family friendly hotel with activities`
                - `business hotel with meeting rooms`
                - `pet friendly accommodation`
                """)
            
            with col2:
                st.markdown("""
                **Intent-Based Search:**
                - `where can I stay for a wedding`
                - `best place for a relaxing vacation`
                - `hotel for conference and events`
                - `quiet retreat in nature`
                """)
    
    # Footer with info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### ℹ️ About
    This app demonstrates Azure AI Search capabilities:
    
    **🔤 Keyword Search:**
    - BM25 ranking algorithm
    - Term frequency analysis
    - Traditional full-text search
    
    **🧠 Semantic Search:**
    - AI-powered query understanding
    - Contextual relevance ranking
    - Extractive captions & answers
    - Reranker scoring
    
    **🎯 Semantic + Filters:**
    - Combines semantic ranking with filters
    - Best precision and recall
    
    **🔄 Auto-Search:**
    - Results update automatically when you change filters or search mode
    - Disable if you prefer manual control
    - Click 🔎 Search button to refresh anytime
    
    Based on the [Azure AI Search Quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal)
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 🆚 Search Mode Comparison
    
    **When to use Keyword:**
    - Exact term matching
    - Known entity search
    - Fast, traditional search
    
    **When to use Semantic:**
    - Natural language queries
    - Intent-based search
    - Understanding context
    
    **When to use Semantic + Filters:**
    - Complex requirements
    - Combining AI and precision
    - Best of both worlds
    """)

if __name__ == "__main__":
    main()
