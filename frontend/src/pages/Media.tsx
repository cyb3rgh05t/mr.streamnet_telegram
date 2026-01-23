import { useEffect, useState } from "react";
import api from "@/lib/api";
import { useCache } from "@/contexts/CacheContext";
import LoadingSpinner from "@/components/LoadingSpinner";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFilm, faSearch } from "@fortawesome/free-solid-svg-icons";

interface MediaItem {
  id: number;
  title: string;
  year?: number;
  status: string;
  poster?: string;
  type: string;
}

const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

export default function Media() {
  const cache = useCache();
  const [sonarrMedia, setSonarrMedia] = useState<MediaItem[]>([]);
  const [radarrMedia, setRadarrMedia] = useState<MediaItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"sonarr" | "radarr">("sonarr");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchMedia();
  }, []);

  const fetchMedia = async () => {
    // Check cache first
    const cachedSonarr = cache.get<MediaItem[]>("media_sonarr");
    const cachedRadarr = cache.get<MediaItem[]>("media_radarr");

    const sonarrStale = cache.isStale("media_sonarr", CACHE_TTL);
    const radarrStale = cache.isStale("media_radarr", CACHE_TTL);

    // Use cached data if available and not stale
    if (cachedSonarr && !sonarrStale) {
      setSonarrMedia(cachedSonarr);
    }
    if (cachedRadarr && !radarrStale) {
      setRadarrMedia(cachedRadarr);
    }

    // If both are cached and fresh, no need to fetch
    if (cachedSonarr && cachedRadarr && !sonarrStale && !radarrStale) {
      setLoading(false);
      return;
    }

    // Fetch fresh data
    try {
      const [sonarrRes, radarrRes] = await Promise.all([
        sonarrStale
          ? api.get("/media/sonarr")
          : Promise.resolve({ data: { items: cachedSonarr } }),
        radarrStale
          ? api.get("/media/radarr")
          : Promise.resolve({ data: { items: cachedRadarr } }),
      ]);

      const sonarrData = sonarrRes.data.items;
      const radarrData = radarrRes.data.items;

      setSonarrMedia(sonarrData);
      setRadarrMedia(radarrData);

      // Update cache
      cache.set("media_sonarr", sonarrData, CACHE_TTL);
      cache.set("media_radarr", radarrData, CACHE_TTL);
    } catch (error) {
      console.error("Failed to fetch media:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading media..." />;
  }

  const currentMedia = activeTab === "sonarr" ? sonarrMedia : radarrMedia;
  const filteredMedia = currentMedia.filter((item) =>
    item.title.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="media-page">
      <div className="page-header">
        <h1>
          <FontAwesomeIcon icon={faFilm} /> Media Library
        </h1>
        <p className="subtitle">Browse your Sonarr and Radarr media</p>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab-button ${activeTab === "sonarr" ? "active" : ""}`}
          onClick={() => setActiveTab("sonarr")}
        >
          Sonarr ({sonarrMedia.length})
        </button>
        <button
          className={`tab-button ${activeTab === "radarr" ? "active" : ""}`}
          onClick={() => setActiveTab("radarr")}
        >
          Radarr ({radarrMedia.length})
        </button>
      </div>

      {/* Search */}
      <div className="search-box">
        <FontAwesomeIcon icon={faSearch} className="search-icon" />
        <input
          type="text"
          placeholder="Search media..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="search-input"
        />
      </div>

      {/* Media Grid */}
      <div
        className={`media-grid ${activeTab === "sonarr" ? "sonarr-grid" : "radarr-grid"}`}
      >
        {filteredMedia.length === 0 ? (
          <div className="empty-state">
            <p>No media found</p>
          </div>
        ) : (
          filteredMedia.map((item) => (
            <div key={item.id} className="media-card">
              {item.poster ? (
                <img
                  src={item.poster}
                  alt={item.title}
                  className={`media-poster ${activeTab === "sonarr" ? "sonarr-poster" : "radarr-poster"}`}
                />
              ) : (
                <div
                  className={`media-poster-placeholder ${activeTab === "sonarr" ? "sonarr-poster" : "radarr-poster"}`}
                >
                  <FontAwesomeIcon icon={faFilm} />
                </div>
              )}
              <div className="media-info">
                <h3 className="media-title">{item.title}</h3>
                {item.year && <p className="media-year">{item.year}</p>}
                <span className={`media-status ${item.status}`}>
                  {item.status}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
