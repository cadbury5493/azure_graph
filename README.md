# Need for Granular CIS Control Reporting Using AWS SSM

## Introduction

Our CIS compliance validation integrates with GCS exception management through Qualys.  
To properly support exception handling and audit requirements, we require **sub-control level granularity** in compliance reporting.

AWS Systems Manager (SSM) provides the necessary detailed control breakdown to support this need.

---

## Example: CIS Control 1.1.1.2

**Control:** Ensure mounting of udf filesystems is disabled

### SSM Output (Detailed)

```json
{
  "id": "1.1.1.2",
  "status": "failed",
  "results": [
    { "status": "passed", "code_desc": "module not loaded" },
    { "status": "failed", "code_desc": "module not disabled" },
    { "status": "passed", "code_desc": "module not blacklisted" }
  ]
}
```

## What SSM Provides

SSM provides:

- Overall control status  
- Individual sub-test results  
- Technical explanation for each sub-test  

This clearly shows:

- Which specific condition failed  
- Why it failed  
- What passed  

---

## Why Granular Reporting Is Required

The GCS team manages exceptions in Qualys where controls are broken down into:

- 1.1.1.2.a  
- 1.1.1.2.b  
- 1.1.1.2.c  

Waivers are applied at the **sub-control level**.

### Example

If **1.1.1.2.b** is waived and only that sub-test fails, we must:

- Recognize the failure is covered under an approved exception  
- Avoid marking the entire control as non-compliant  
- Maintain accurate audit traceability  

Without sub-test visibility, this mapping cannot be performed accurately.

---

## Benefits of Using SSM Detailed Results

Leveraging SSM granular output enables:

- Precise waiver-to-sub-control mapping  
- Clear audit evidence  
- Accurate compliance posture reporting  
- Faster root cause analysis  
- Automated exception reconciliation  

This prevents over-reporting of risk and reduces manual investigation.

---

## Conclusion

Granular, sub-control level reporting is essential for:

- Aligning with Qualys exception management  
- Supporting audit requirements  
- Providing accurate compliance status  
- Enabling automated governance workflows  

AWS SSM provides the detailed control breakdown required to meet these objectives.
