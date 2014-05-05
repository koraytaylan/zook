import json

AValues = (
    (
        (0, 1.42, 2.24, 2.82, 3.24, 3.54, 3.76, 3.9, 3.96, 3.96, 3.96),
        (0, 1.58, 3.00, 4.34, 5.52, 6.62, 7.56, 8.42, 9.12, 9.74, 10.20),
        (0, 1.82, 3.24, 4.34, 5.28, 6.06, 6.72, 7.26, 7.68, 7.98, 8.16),
        (0, 1.42, 2.44, 3.22, 3.80, 4.22, 4.56, 4.82, 5.00, 5.10, 5.12),
        (0, 1.42, 2.24, 2.82, 3.24, 3.54, 3.76, 3.90, 3.96, 3.96, 3.96),
        (0, 0.50, 0.84, 1.06, 1.20, 1.30, 1.32, 1.32, 1.32, 1.32, 1.32)
    ),
    (
        (0, 1.60, 2.60, 3.36, 3.96, 4.44, 4.84, 5.16, 5.40, 5.56, 5.64),
        (0, 1.76, 3.36, 4.88, 6.24, 7.52, 8.64, 9.68, 10.56, 11.36, 12.00),
        (0, 2.00, 3.60, 4.88, 6.00, 6.96, 7.80, 8.52, 9.12, 9.60, 9.96),
        (0, 1.60, 2.80, 3.76, 4.52, 5.12, 5.64, 6.08, 6.44, 6.72, 6.92),
        (0, 1.60, 2.60, 3.36, 3.96, 4.44, 4.84, 5.16, 5.40, 5.56, 5.64),
        (0, 0.68, 1.20, 1.60, 1.92, 2.20, 2.40, 2.56, 2.68, 2.76, 2.80)
    ),
    (
        (0, 2.00, 3.25, 4.20, 4.95, 5.55, 6.05, 6.45, 6.75, 6.95, 7.05),
        (0, 2.20, 4.20, 6.10, 7.80, 9.40, 10.80, 12.10, 13.20, 14.20, 15.00),
        (0, 2.50, 4.50, 6.10, 7.50, 8.70, 9.75, 10.65, 11.40, 12.00, 12.45),
        (0, 2.00, 3.50, 4.70, 5.65, 6.40, 7.05, 7.60, 8.05, 8.40, 8.65),
        (0, 2.00, 3.25, 4.20, 4.95, 5.55, 6.05, 6.45, 6.75, 6.95, 7.05),
        (0, 0.85, 1.50, 2.00, 2.40, 2.75, 3.00, 3.20, 3.35, 3.45, 3.50)
    ),
    (
        (0, 2.30, 3.85, 5.10, 6.15, 7.05, 7.85, 8.55, 9.15, 9.65, 10.05),
        (0, 2.50, 4.80, 7.00, 9.00, 10.90, 12.60, 14.20, 15.60, 16.90, 18.00),
        (0, 2.80, 5.10, 7.00, 8.70, 10.20, 11.55, 12.75, 13.80, 14.70, 15.45),
        (0, 2.30, 4.10, 5.60, 6.85, 7.90, 8.85, 9.70, 10.45, 11.10, 11.65),
        (0, 2.30, 3.85, 5.10, 6.15, 7.05, 7.85, 8.55, 9.15, 9.65, 10.05),
        (0, 1.15, 2.10, 2.90, 3.60, 4.25, 4.80, 5.30, 5.75, 6.15, 6.50)
    )
)
AValueUp = []
s = -1
for i in AValues:
    s += 1
    r = -1
    rs = []
    for j in i:
        r += 1
        q = -1
        qs = []
        for k in j:
            q += 1
            if q + 1 < len(j):
                qs.append(AValues[s][r][q + 1] - k)
        rs.append(qs)
    AValueUp.append(rs)
print(json.dumps(AValueUp))