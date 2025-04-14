# Copyright 2025 TigerGraph Inc.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file or https://www.apache.org/licenses/LICENSE-2.0
#
# Permission is granted to use, copy, modify, and distribute this software
# under the License. The software is provided "AS IS", without warranty.

from typing import Dict, Optional
from pydantic import BaseModel, Field


TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION = """
Configuration for connecting to a TigerGraph instance.

All fields can either be populated **from environment variables** (recommended) or **explicitly provided**.  
**Do not provide both**—either use the environment variables **or** explicitly pass the values.

If environment variables are not found, it is recommended to set the environment variables or explicitly provide the necessary parameters.

The following environment variables are used (with their corresponding defaults if not set):

- `TG_HOST` (default: `http://127.0.0.1`)
- `TG_RESTPP_PORT` (default: `14240`)
- `TG_GSQL_PORT` (default: `14240`)
- `TG_USERNAME`
- `TG_PASSWORD`
- `TG_SECRET`
- `TG_TOKEN`

Supported authentication modes (choose **only one** method):

1. **Username/password authentication**
```json
{
  "host": "http://localhost",
  "username": "tigergraph",
  "password": "tigergraph",
  "restpp_port": 14240,   // Optional
  "gsql_port": 14240      // Optional
}
```

2. **Secret-based authentication**
```json
{
  "host": "http://localhost",
  "secret": "YOUR_SECRET",
  "restpp_port": 14240,   // Optional
  "gsql_port": 14240      // Optional
}
```

3. **Token-based authentication**
```json
{
  "host": "http://localhost",
  "token": "YOUR_API_TOKEN",
  "restpp_port": 14240,   // Optional
  "gsql_port": 14240      // Optional
}
```

⚠️ **Important:** Only one authentication method should be used at a time.
"""


class BaseToolInput(BaseModel):
    """Base input shared by all TigerGraphX tools."""

    tigergraph_connection_config: Optional[Dict] = Field(
        default=None, description=TIGERGRAPH_CONNECTION_CONFIG_DESCRIPTION.strip()
    )
