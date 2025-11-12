# Azure AI Search - Advanced Hotels Search UI

An enhanced Streamlit-based search interface showcasing three search modes: **Keyword**, **Semantic**, and **Semantic + Filters** for Azure AI Search with the hotels dataset.

## 🎯 Features

### Three Search Modes

#### 1. 🔤 Keyword Search
- **Traditional BM25 ranking** based on term frequency
- Fast and efficient for exact term matching
- Best for known entity searches (e.g., hotel names, locations)
- Standard full-text search capabilities

#### 2. 🧠 Semantic Search
- **AI-powered query understanding** using Microsoft's semantic models
- Understands natural language and query intent
- Provides **extractive captions** highlighting relevant content
- Shows **reranker scores** for semantic relevance
- Generates **AI answers** from search results
- Perfect for conversational queries

#### 3. 🎯 Semantic + Filters
- **Combines semantic ranking with traditional filters**
- Best of both worlds: AI understanding + precise filtering
- Apply rating, parking, and category filters while maintaining semantic relevance
- Ideal for complex search requirements

### Enhanced UI Features

- **Search Mode Dropdown**: Easy switching between search modes
- **Relevance Scores**: View BM25 scores and semantic reranker scores
- **Extractive Captions**: See relevant excerpts for semantic searches
- **AI-Generated Answers**: Get direct answers from semantic search
- **Dynamic Examples**: Context-aware example queries for each mode
- **Category Filter**: Multi-select hotel categories
- **Expandable Descriptions**: Clean card layout with collapsible details
- **Mode-Specific Help**: Contextual information for each search mode

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Azure AI Search

Follow the [Azure AI Search Quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal?pivots=import-data-new) to create your search service and load the hotels data.

### 3. Enable Semantic Search (Optional)

To use Semantic and Semantic + Filters modes:

1. Go to your Azure Search service in the Azure Portal
2. Select your index (`hotels-sample-index`)
3. Go to **Semantic configurations** tab
4. Click **Add semantic configuration**
5. Name it `my-semantic-config`
6. Configure:
   - **Title field**: `HotelName`
   - **Content fields**: `Description`, `Category`
   - **Keyword fields**: `Tags`
7. Save the configuration

> **Note**: Semantic search requires a **Basic tier or higher** (not available on Free tier)

### 4. Configure Environment

```bash
cp env.sample .env
# Edit .env with your credentials
```

Example `.env`:
```
AZURE_SEARCH_ENDPOINT='https://your-service.search.windows.net'
AZURE_SEARCH_API_KEY='your-admin-api-key'
AZURE_SEARCH_INDEX_NAME='hotels-sample-index'
AZURE_SEARCH_SEMANTIC_CONFIG='my-semantic-config'
```

### 5. Run the Application

```bash
streamlit run azure_search_hotels_ui.py
```

## 📊 Search Mode Comparison

| Feature | Keyword | Semantic | Semantic + Filters |
|---------|---------|----------|-------------------|
| **Speed** | ⚡ Fastest | 🐢 Slower | 🐢 Slower |
| **Accuracy** | Good for exact matches | Excellent for intent | Best overall |
| **Query Type** | Keywords | Natural language | Natural language |
| **Filters** | ✅ Yes | ❌ No | ✅ Yes |
| **AI Captions** | ❌ No | ✅ Yes | ✅ Yes |
| **AI Answers** | ❌ No | ✅ Yes | ✅ Yes |
| **Reranker** | ❌ No | ✅ Yes | ✅ Yes |
| **Use Case** | Known searches | Exploratory | Complex requirements |

## 💡 Example Searches by Mode

### Keyword Search Examples
Perfect for specific terms and known entities:
- `beach` - Find hotels near beaches
- `spa luxury` - Hotels with spa and luxury amenities
- `Seattle downtown` - Hotels in downtown Seattle
- `business center wifi` - Business-focused hotels

### Semantic Search Examples
Natural language queries that understand intent:
- `romantic getaway near the ocean` - Understands romantic + ocean
- `family friendly hotel with activities` - Identifies family needs
- `where can I stay for a wedding` - Understands event context
- `best place for a relaxing vacation` - Intent-based search
- `quiet retreat in nature` - Contextual understanding

### Semantic + Filters Examples
Combine natural language with precise requirements:
- Query: `romantic beachfront property`
  - Filters: Rating ≥ 4.5, Parking, Category: Luxury
- Query: `business hotel with conference rooms`
  - Filters: Rating ≥ 4.0, Category: Suite or Boutique
- Query: `family vacation spot`
  - Filters: Rating ≥ 4.0, Parking

## 🎨 UI Components

### Search Configuration Panel
- **Search Mode Selector**: Dropdown with descriptive labels
- **Show Relevance Scores**: Toggle score display
- **Mode Information**: Context-aware help text

### Sidebar Filters
- **Rating Slider**: Filter by minimum rating (1-5 stars)
- **Parking Checkbox**: Show only hotels with parking
- **Category Multi-Select**: Choose from Budget, Boutique, Luxury, Resort, Suite
- **Results Slider**: Control number of results (5-50)
- **Filter Status**: Visual indicator when filters are disabled (pure semantic mode)

### Results Display
- **Result Counter**: Total matches with mode emoji
- **AI Answers**: Extractive answers for semantic searches (displayed first)
- **Hotel Cards**: Comprehensive information cards
  - Hotel name with optional search score
  - Semantic reranker score (semantic modes)
  - Extractive captions (semantic modes)
  - Category and tags
  - Expandable full description
  - Address, rating, parking, renovation date

### Help & Examples
- **Dynamic Examples**: Mode-specific example queries
- **Search Mode Comparison**: When to use each mode
- **About Section**: Feature explanations

## 🔧 Technical Details

### Semantic Search Implementation

The app uses Azure AI Search's semantic ranking capabilities:

```python
# Semantic search configuration
search_params = {
    "query_type": QueryType.SEMANTIC,
    "semantic_configuration_name": "my-semantic-config",
    "query_caption": QueryCaptionType.EXTRACTIVE,
    "query_answer": QueryAnswerType.EXTRACTIVE
}
```

### Scoring Systems

1. **BM25 Score** (Keyword): `@search.score`
   - Based on term frequency and inverse document frequency
   - Higher score = better keyword match

2. **Reranker Score** (Semantic): `@search.reranker_score`
   - AI-powered semantic relevance score
   - Considers query intent and context
   - Typically ranges from 0-4+

### Captions and Answers

- **Captions**: Relevant excerpts from documents with highlighting
- **Answers**: Direct answers extracted from top results
- Both generated by Microsoft's semantic models

## 📈 Performance Considerations

### Keyword Search
- **Latency**: 10-50ms typical
- **Cost**: Standard search pricing
- **Scale**: Handles high query volume

### Semantic Search
- **Latency**: 100-300ms typical (includes reranking)
- **Cost**: Additional semantic search pricing
- **Scale**: Limited queries per second (depends on tier)
- **Requirements**: Basic tier or higher

## 🐛 Troubleshooting

### "The field 'X' in the search field list is not searchable"
- **Status**: ✅ **FIXED** - This error has been resolved!
- **What happened**: Some index fields aren't marked as "Searchable"
- **Solution Applied**: Code now lets Azure Search automatically use all searchable fields
- **No action required**: The app handles this automatically
- **Details**: See `WORKAROUND_NONSEARCHABLE_FIELDS.md` for full explanation

### "No hotels found" / Search returns 0 results
- **Common causes**:
  1. Search term doesn't exist in your data's searchable fields
  2. Filters are too restrictive (rating, parking, category)
  3. Only certain fields are searchable (typically Description, Tags, Category)
- **Solutions**:
  - Remove all filters first
  - Try common terms: "beach", "luxury", "spa", "view"
  - Use `*` to show all hotels (verifies connection)
  - Run `verify_search_index.py` to check your data
  - Enable debug mode in Advanced Options to see what's being searched

### "Semantic configuration error"
- **Cause**: Index doesn't have semantic search configured
- **Solution**: 
  1. Check if you're on Basic tier or higher (not Free)
  2. Create semantic configuration in Azure Portal
  3. Use "Keyword" mode if semantic search isn't available

### "Filters disabled in Semantic Search mode"
- **Expected behavior**: Pure semantic mode doesn't support filters
- **Solution**: Use "Semantic + Filters" mode instead

### No captions or answers displayed
- **Causes**:
  1. Semantic configuration not properly set up
  2. Query too generic
  3. No relevant content found
- **Solution**: 
  - Verify semantic configuration exists
  - Try more specific queries
  - Check that content fields are configured

### Poor semantic results
- **Causes**:
  1. Query not well-formed
  2. Content fields not optimized
  3. Need more descriptive content
- **Solutions**:
  - Use natural language questions
  - Ensure Description field has rich content
  - Configure title/content/keyword fields properly

## 🎓 Learning Resources

### Azure AI Search
- [Semantic Search Overview](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)
- [Configure Semantic Ranking](https://learn.microsoft.com/en-us/azure/search/semantic-how-to-query-request)
- [Query Types](https://learn.microsoft.com/en-us/azure/search/search-query-overview)

### Semantic Search Concepts
- [How Semantic Ranking Works](https://learn.microsoft.com/en-us/azure/search/semantic-ranking)
- [Semantic Answers](https://learn.microsoft.com/en-us/azure/search/semantic-answers)
- [Semantic Captions](https://learn.microsoft.com/en-us/azure/search/semantic-how-to-query-request#semantic-captions)

### Pricing
- [Azure AI Search Pricing](https://azure.microsoft.com/en-us/pricing/details/search/)
- [Semantic Search Pricing](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview#pricing)

## 🚀 Advanced Enhancements

### Potential Extensions

1. **Hybrid Search**: Add vector search capabilities
2. **Autocomplete**: Implement type-ahead suggestions
3. **Faceted Navigation**: Add category/tag facets
4. **Result Highlighting**: Highlight matching terms
5. **Search Analytics**: Track queries and results
6. **Personalization**: User preferences and history
7. **Geographic Search**: Add map-based location filtering
8. **Multi-language**: Support multiple languages
9. **Export Results**: Download results as CSV/JSON
10. **Compare Hotels**: Side-by-side comparison feature

### Custom Scoring Profiles

Enhance keyword search with custom scoring:
```python
# Add scoring profile in Azure Portal
{
    "name": "hotels-scoring",
    "functions": [
        {
            "type": "magnitude",
            "fieldName": "Rating",
            "boost": 5,
            "interpolation": "linear"
        }
    ]
}
```

## 📝 Code Structure

```
azure_search_hotels_ui.py
├── Configuration
│   ├── Environment variables
│   └── Search client initialization
├── Core Functions
│   ├── perform_search() - Multi-mode search
│   ├── format_address() - Address formatting
│   └── display_hotel_card() - Result display
└── Streamlit UI
    ├── Header and mode selection
    ├── Search input
    ├── Sidebar filters
    ├── Results display
    └── Help sections
```

## 🤝 Contributing

Suggestions for improvements:
- Additional filter types
- Better visualization of scores
- Enhanced semantic configuration
- Performance optimizations
- UI/UX improvements

## 📄 License

This demo application is provided as-is for educational purposes.

---

**Happy Searching! 🎉**

For questions or issues, refer to the [Azure AI Search documentation](https://learn.microsoft.com/en-us/azure/search/).
