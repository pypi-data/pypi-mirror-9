local key = KEYS[1]
local data = ARGV[1]
local model = ARGV[2]
local dnf = cjson.decode(ARGV[3])
local timeout = ARGV[4]
local inv_timeout = ARGV[5]

-- Update schemes
-- NOTE: dnf could be empty for reliably empty query
if next(dnf) ~= nil then
    local schemes = {}
    for _, conj in ipairs(dnf) do
        local s = {}
        for _, eq in ipairs(conj) do
            table.insert(s, eq[1])
        end
        table.insert(schemes, table.concat(s, ','))
    end
    redis.call('sadd', 'schemes:' .. model, unpack(schemes))
end

-- Write data to cache
redis.call('setex', key, timeout, data)

local conj_cache_key = function (model, conj)
    local parts = {}
    for _, eq in ipairs(conj) do
        table.insert(parts, eq[1] .. '=' .. tostring(eq[2]))
    end

    return 'conj:' .. model .. ':' .. table.concat(parts, '&')
end

-- Add new cache_key to list of dependencies for every conjunction in dnf
for _, conj in ipairs(dnf) do
    local conj_key = conj_cache_key(model, conj)
    redis.call('sadd', conj_key, key)
    redis.call('expire', conj_key, inv_timeout)
end
