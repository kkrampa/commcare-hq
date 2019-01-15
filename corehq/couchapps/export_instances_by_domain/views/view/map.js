function(doc) {
    if (doc.doc_type === "FormExportInstance" || doc.doc_type === "CaseExportInstance") {
        emit([doc.domain, doc.doc_type, doc.is_deidentified], {
            _id: doc._id,
            domain: doc.domain,
            doc_type: doc.doc_type,
            is_deidentified: doc.is_deidentified,
            is_daily_saved_export: doc.is_daily_saved_export,
            export_format: doc.export_format,
            name: doc.name,
        });
    }
}
