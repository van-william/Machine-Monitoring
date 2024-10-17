function toInfluxDBFormat(measurement, tags, fields, timestamp = null) {
    // Validate input
    if (typeof measurement !== 'string' || measurement.length === 0) {
      throw new Error('Measurement must be a non-empty string');
    }
    if (typeof tags !== 'object' || typeof fields !== 'object') {
      throw new Error('Tags and fields must be objects');
    }
    if (Object.keys(fields).length === 0) {
      throw new Error('At least one field is required');
    }
  
    // Escape special characters in measurement
    const escapedMeasurement = measurement.replace(/,|\s/g, '\\$&');
  
    // Process tags
    const tagString = Object.entries(tags)
      .map(([key, value]) => `${escapeKey(key)}=${escapeValue(value)}`)
      .join(',');
  
    // Process fields
    const fieldString = Object.entries(fields)
      .map(([key, value]) => `${escapeKey(key)}=${formatValue(value)}`)
      .join(',');
  
    // Construct the line protocol string
    let lineProtocol = escapedMeasurement;
    if (tagString) lineProtocol += `,${tagString}`;
    lineProtocol += ` ${fieldString}`;
    if (timestamp !== null) lineProtocol += ` ${timestamp}`;
  
    return lineProtocol;
  }
  
  function escapeKey(key) {
    return key.replace(/,|=|\s/g, '\\$&');
  }
  
  function escapeValue(value) {
    return String(value).replace(/,|=|\s/g, '\\$&');
  }
  
  function formatValue(value) {
    if (typeof value === 'string') return `"${value.replace(/"/g, '\\"')}"`;
    if (typeof value === 'number') return isFinite(value) ? String(value) : 'null';
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    return 'null';
  }
  
  // Example usage
  const measurement = "fan";
  const tags = { location: 'Chicago', sensor: 'S1' };
  const fields = { temperature: 72.5, humidity: 60, description: 'Partly cloudy', current:msg.payload};
  
  const influxDBLine = toInfluxDBFormat(measurement, tags, fields);
  msg.payload = influxDBLine;
  return msg;