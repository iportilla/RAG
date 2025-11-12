# Azure AI Search - Hotels Search UI

A Streamlit-based search interface for Azure AI Search demonstrating keyword search, filtering, and faceted navigation using the hotels sample dataset.

## 📋 Prerequisites

1. **Azure Subscription**: You need an active Azure subscription
2. **Azure AI Search Service**: Create a search service in Azure Portal
3. **Hotels Sample Data**: Loaded into your search index

## 🚀 Setup Instructions

### Step 1: Create Azure AI Search Service

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a new **Azure AI Search** service
3. Note your service endpoint (e.g., `https://your-service.search.windows.net`)
4. Get your Admin API Key from the **Keys** section

### Step 2: Load Hotels Sample Data

Follow the [Azure AI Search Quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal?pivots=import-data-new) to:

1. Create an Azure Storage account
2. Create a container named `hotels-sample`
3. Upload the [sample hotels JSON data](https://github.com/Azure-Samples/azure-search-sample-data/blob/main/hotels/HotelsData_toAzureBlobs.json)
4. Use the **Import data (new)** wizard in Azure Portal to:
   - Connect to your storage account
   - Select **Keyword search**
   - Configure the index with these field attributes:

| Field | Attributes |
|-------|-----------|
| HotelId | Key, Retrievable, Filterable, Sortable, Searchable |
| HotelName, Category | Retrievable, Filterable, Sortable, Searchable |
| Description | Retrievable, Searchable |
| Tags | Retrievable, Filterable, Searchable |
| ParkingIncluded, Rating | Retrievable, Filterable, Sortable |
| Address.* | Retrievable, Filterable, Searchable |

5. Name your index `hotels-sample-index` (or update `.env` with your index name)

### Step 3: Configure Environment

1. Copy `env.sample` to `.env`:
   ```bash
   cp env.sample .env
   ```

2. Edit `.env` and add your credentials:
   ```
   AZURE_SEARCH_ENDPOINT='https://your-service.search.windows.net'
   AZURE_SEARCH_API_KEY='your-admin-api-key'
   AZURE_SEARCH_INDEX_NAME='hotels-sample-index'
   ```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎯 Running the Application

```bash
streamlit run azure_search_hotels_ui.py
```

The app will open in your browser at `http://localhost:8501`

## 🔍 Features

### Search Capabilities
- **Full-text search**: Search across hotel names, descriptions, and tags
- **Keyword matching**: Find hotels by amenities, features, or location
- **Empty search**: Use `*` to show all hotels

### Filtering
- **Rating filter**: Show hotels with minimum rating (1-5 stars)
- **Parking filter**: Show only hotels with parking included
- **Combinable filters**: Apply multiple filters simultaneously

### Results Display
- **Hotel cards** with comprehensive information:
  - Hotel name and category
  - Description
  - Tags (amenities/features)
  - Address
  - Rating
  - Parking availability
  - Last renovation date
- **Total count** of matching results
- **Adjustable results**: Show 5-50 results

## 💡 Example Searches

### By Keyword
- `beach` - Find beachfront hotels
- `spa` - Find hotels with spa facilities
- `luxury` - Find luxury hotels
- `historic` - Find historic properties

### By Feature
- `pool` - Hotels with swimming pools
- `wifi` - Hotels with WiFi
- `restaurant` - Hotels with restaurants
- `business center` - Hotels with business facilities

### By Location
- `Seattle` - Hotels in Seattle
- `San Francisco` - Hotels in San Francisco
- `New York` - Hotels in New York

### Advanced Queries
You can combine searches with filters:
- Search: `beach` + Rating: 4.0+ + Parking: Yes
- Search: `spa` + Rating: 4.5+
- Search: `historic` + Parking: Yes

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
│  (Web Browser)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼─────────────┐
│  Azure AI Search API │
│   (Search Service)   │
└────────┬─────────────┘
         │
         │ Indexer
         │
┌────────▼────────────┐
│  Azure Blob Storage │
│  (Hotels JSON Data) │
└─────────────────────┘
```

## 📚 Azure AI Search Concepts

### Index
The searchable data structure containing hotel documents with defined fields and attributes.

### Searchable Fields
Fields that support full-text search:
- HotelName
- Description
- Category
- Tags
- Address fields

### Filterable Fields
Fields that can be used in filter expressions:
- Rating
- ParkingIncluded
- Category
- Tags

### Retrievable Fields
Fields returned in search results (most fields in this demo).

## 🔧 Customization

### Adding More Filters
Edit `azure_search_hotels_ui.py` to add filters for:
- Last renovation date range
- Specific categories
- Geographic location (requires geospatial setup)
- Price range (if Rooms.BaseRate is indexed)

### Changing Display
Modify `display_hotel_card()` function to:
- Show room information
- Add images (if URLs are in data)
- Display additional amenities
- Show pricing information

### Advanced Search Features
You can extend the app with:
- **Faceted navigation**: Show category counts
- **Autocomplete**: Suggest queries as user types
- **Semantic search**: Enable semantic ranking
- **Scoring profiles**: Custom relevance scoring

## 🐛 Troubleshooting

### "Please configure Azure Search credentials"
- Ensure `.env` file exists and has correct values
- Check that endpoint includes `https://` protocol
- Verify API key is the Admin key (not Query key)

### "Failed to initialize search client"
- Verify your search service is running
- Check network connectivity
- Ensure endpoint URL is correct

### "No hotels found"
- Verify data was loaded via Import wizard
- Check index name matches `.env` configuration
- Try search term `*` to show all documents
- Verify indexer ran successfully in Azure Portal

### Import Errors
- Run: `pip install -r requirements.txt`
- Use Python 3.8 or higher
- Consider using a virtual environment

## 📖 Additional Resources

- [Azure AI Search Documentation](https://learn.microsoft.com/en-us/azure/search/)
- [Azure Search Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/search-documents-readme)
- [Hotels Quickstart Guide](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal)
- [Sample Hotels Data](https://github.com/Azure-Samples/azure-search-sample-data/tree/main/hotels)
- [Query Syntax](https://learn.microsoft.com/en-us/azure/search/query-simple-syntax)

## 📝 License

This demo application is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to extend this demo with additional features:
- Geographic search
- Advanced filtering
- Result highlighting
- Export functionality
- Comparison features
